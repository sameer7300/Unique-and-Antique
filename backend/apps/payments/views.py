"""
Views for the payments app.
"""

from rest_framework import generics, viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from decimal import Decimal
import stripe
from django.conf import settings

from .models import (
    Payment, PaymentRefund, PaymentMethod, PaymentWebhook, PaymentTransaction
)
from .serializers import (
    PaymentListSerializer, PaymentDetailSerializer, PaymentCreateSerializer,
    PaymentRefundSerializer, PaymentRefundCreateSerializer, PaymentMethodSerializer,
    PaymentMethodCreateSerializer, PaymentWebhookSerializer, PaymentIntentSerializer,
    PaymentConfirmSerializer, PaymentStatsSerializer, BulkPaymentUpdateSerializer,
    CODPaymentSerializer, PaymentReportSerializer
)
from apps.orders.models import Order
from utils.permissions import IsOwnerOrReadOnly, IsStaffOrAdmin, CanProcessPayments
from utils.pagination import StandardResultsSetPagination
from utils.exceptions import PaymentProcessingError

# Initialize Stripe
stripe.api_key = settings.STRIPE_SECRET_KEY


class PaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing payments.
    """
    permission_classes = [IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['provider', 'status', 'payment_type']
    search_fields = ['order__order_number', 'provider_payment_id']
    ordering_fields = ['created_at', 'amount', 'status']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Get payments based on user permissions."""
        if self.request.user.is_staff:
            return Payment.objects.select_related('order__user').prefetch_related(
                'refunds', 'transactions'
            )
        else:
            return Payment.objects.filter(
                order__user=self.request.user
            ).select_related('order').prefetch_related('refunds', 'transactions')
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return PaymentListSerializer
        elif self.action == 'retrieve':
            return PaymentDetailSerializer
        elif self.action == 'create':
            return PaymentCreateSerializer
        return PaymentDetailSerializer
    
    def get_permissions(self):
        """Get permissions based on action."""
        if self.action in ['create', 'list', 'retrieve']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [CanProcessPayments]
        
        return [permission() for permission in permission_classes]
    
    def create(self, request, *args, **kwargs):
        """Create a new payment."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    order = serializer.validated_data['order']
                    provider = serializer.validated_data['provider']
                    amount = serializer.validated_data['amount']
                    
                    # Create payment record
                    payment = Payment.objects.create(
                        order=order,
                        provider=provider,
                        amount=amount,
                        currency=serializer.validated_data.get('currency', 'USD'),
                        billing_address=serializer.validated_data.get('billing_address', {}),
                        metadata=serializer.validated_data.get('metadata', {})
                    )
                    
                    # Process payment based on provider
                    if provider == 'stripe':
                        payment = self._process_stripe_payment(payment, request.data)
                    elif provider == 'cod':
                        payment = self._process_cod_payment(payment)
                    else:
                        raise PaymentProcessingError(f"Unsupported payment provider: {provider}")
                    
                    response_serializer = PaymentDetailSerializer(
                        payment,
                        context={'request': request}
                    )
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    
            except PaymentProcessingError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_stripe_payment(self, payment, request_data):
        """Process Stripe payment."""
        try:
            # Create payment intent
            intent = stripe.PaymentIntent.create(
                amount=int(payment.amount * 100),  # Convert to cents
                currency=payment.currency.lower(),
                metadata={
                    'order_id': payment.order.id,
                    'payment_id': str(payment.payment_id)
                }
            )
            
            payment.provider_payment_intent_id = intent.id
            payment.status = 'processing'
            payment.save()
            
            # Create transaction record
            PaymentTransaction.objects.create(
                payment=payment,
                action='authorize',
                amount=payment.amount,
                currency=payment.currency,
                provider_transaction_id=intent.id,
                response_data=intent
            )
            
            return payment
            
        except stripe.error.StripeError as e:
            payment.status = 'failed'
            payment.failure_reason = str(e)
            payment.save()
            raise PaymentProcessingError(f"Stripe error: {str(e)}")
    
    def _process_cod_payment(self, payment):
        """Process Cash on Delivery payment."""
        payment.status = 'pending'
        payment.save()
        
        # Create transaction record
        PaymentTransaction.objects.create(
            payment=payment,
            action='authorize',
            amount=payment.amount,
            currency=payment.currency,
            status='pending'
        )
        
        return payment
    
    @action(detail=True, methods=['post'])
    def confirm(self, request, pk=None):
        """Confirm payment (for Stripe)."""
        payment = self.get_object()
        
        if payment.provider != 'stripe':
            return Response(
                {'error': 'Payment confirmation only available for Stripe payments'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = PaymentConfirmSerializer(data=request.data)
        if serializer.is_valid():
            try:
                # Confirm payment intent
                intent = stripe.PaymentIntent.confirm(
                    payment.provider_payment_intent_id,
                    payment_method=serializer.validated_data.get('payment_method_id')
                )
                
                if intent.status == 'succeeded':
                    payment.status = 'succeeded'
                    payment.processed_at = timezone.now()
                    payment.provider_payment_id = intent.id
                elif intent.status == 'requires_action':
                    payment.status = 'processing'
                else:
                    payment.status = 'failed'
                    payment.failure_reason = f"Payment intent status: {intent.status}"
                
                payment.save()
                
                # Create transaction record
                PaymentTransaction.objects.create(
                    payment=payment,
                    action='capture' if intent.status == 'succeeded' else 'authorize',
                    amount=payment.amount,
                    currency=payment.currency,
                    status='succeeded' if intent.status == 'succeeded' else 'pending',
                    provider_transaction_id=intent.id,
                    response_data=intent
                )
                
                response_serializer = PaymentDetailSerializer(
                    payment,
                    context={'request': request}
                )
                return Response(response_serializer.data)
                
            except stripe.error.StripeError as e:
                payment.status = 'failed'
                payment.failure_reason = str(e)
                payment.save()
                
                return Response(
                    {'error': f"Stripe error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'], permission_classes=[CanProcessPayments])
    def refund(self, request, pk=None):
        """Create a refund for payment."""
        payment = self.get_object()
        serializer = PaymentRefundCreateSerializer(
            data=request.data,
            context={'payment': payment}
        )
        
        if serializer.is_valid():
            try:
                with transaction.atomic():
                    refund = PaymentRefund.objects.create(
                        payment=payment,
                        amount=serializer.validated_data['amount'],
                        reason=serializer.validated_data.get('reason', ''),
                        admin_notes=serializer.validated_data.get('admin_notes', '')
                    )
                    
                    # Process refund based on provider
                    if payment.provider == 'stripe':
                        self._process_stripe_refund(refund)
                    elif payment.provider == 'cod':
                        self._process_cod_refund(refund)
                    
                    response_serializer = PaymentRefundSerializer(refund)
                    return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                    
            except PaymentProcessingError as e:
                return Response(
                    {'error': str(e)},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _process_stripe_refund(self, refund):
        """Process Stripe refund."""
        try:
            stripe_refund = stripe.Refund.create(
                payment_intent=refund.payment.provider_payment_intent_id,
                amount=int(refund.amount * 100),  # Convert to cents
                metadata={
                    'refund_id': str(refund.refund_id),
                    'order_id': refund.payment.order.id
                }
            )
            
            refund.provider_refund_id = stripe_refund.id
            refund.status = 'succeeded' if stripe_refund.status == 'succeeded' else 'processing'
            refund.processed_at = timezone.now() if stripe_refund.status == 'succeeded' else None
            refund.save()
            
        except stripe.error.StripeError as e:
            refund.status = 'failed'
            refund.save()
            raise PaymentProcessingError(f"Stripe refund error: {str(e)}")
    
    def _process_cod_refund(self, refund):
        """Process COD refund (manual process)."""
        refund.status = 'pending'
        refund.save()
    
    @action(detail=False, methods=['get'], permission_classes=[IsStaffOrAdmin])
    def stats(self, request):
        """Get payment statistics."""
        from django.db.models import Count, Sum, Avg
        
        stats = {
            'total_payments': Payment.objects.count(),
            'successful_payments': Payment.objects.filter(status='succeeded').count(),
            'failed_payments': Payment.objects.filter(status='failed').count(),
            'pending_payments': Payment.objects.filter(status='pending').count(),
            'total_amount': Payment.objects.filter(
                status='succeeded'
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00'),
            'total_refunds': PaymentRefund.objects.filter(status='succeeded').count(),
            'total_refund_amount': PaymentRefund.objects.filter(
                status='succeeded'
            ).aggregate(
                total=Sum('amount')
            )['total'] or Decimal('0.00'),
            'average_payment_amount': Payment.objects.aggregate(
                avg=Avg('amount')
            )['avg'] or Decimal('0.00'),
            'success_rate': 0.0
        }
        
        # Calculate success rate
        total = stats['total_payments']
        if total > 0:
            stats['success_rate'] = round(
                (stats['successful_payments'] / total) * 100, 2
            )
        
        serializer = PaymentStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['post'], permission_classes=[CanProcessPayments])
    def bulk_update(self, request):
        """Bulk payment operations."""
        serializer = BulkPaymentUpdateSerializer(data=request.data)
        if serializer.is_valid():
            payment_ids = serializer.validated_data['payment_ids']
            action = serializer.validated_data['action']
            
            payments = Payment.objects.filter(id__in=payment_ids)
            processed_count = 0
            
            with transaction.atomic():
                if action == 'refund':
                    refund_amount = serializer.validated_data['refund_amount']
                    reason = serializer.validated_data.get('reason', 'Bulk refund')
                    
                    for payment in payments:
                        if payment.is_refundable:
                            try:
                                refund = payment.create_refund(refund_amount, reason)
                                if payment.provider == 'stripe':
                                    self._process_stripe_refund(refund)
                                processed_count += 1
                            except Exception:
                                continue
                
                elif action == 'cancel':
                    for payment in payments:
                        if payment.status in ['pending', 'processing']:
                            payment.status = 'cancelled'
                            payment.save()
                            processed_count += 1
            
            return Response({
                'message': f'{processed_count} payments processed successfully',
                'processed_count': processed_count
            })
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentMethodViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing saved payment methods.
    """
    serializer_class = PaymentMethodSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get payment methods for current user."""
        return PaymentMethod.objects.filter(
            user=self.request.user,
            is_active=True
        )
    
    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'create':
            return PaymentMethodCreateSerializer
        return PaymentMethodSerializer
    
    def perform_create(self, serializer):
        """Create payment method for current user."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_default(self, request, pk=None):
        """Set payment method as default."""
        payment_method = self.get_object()
        
        # Remove default from other payment methods
        PaymentMethod.objects.filter(
            user=request.user,
            is_default=True
        ).update(is_default=False)
        
        # Set this as default
        payment_method.is_default = True
        payment_method.save()
        
        serializer = self.get_serializer(payment_method)
        return Response({
            'message': 'Payment method set as default',
            'payment_method': serializer.data
        })


class PaymentIntentView(generics.CreateAPIView):
    """
    View for creating payment intents (Stripe).
    """
    serializer_class = PaymentIntentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create payment intent."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order_id = serializer.validated_data['order_id']
                order = Order.objects.get(id=order_id, user=request.user)
                
                # Create Stripe payment intent
                intent = stripe.PaymentIntent.create(
                    amount=int(order.total_amount * 100),  # Convert to cents
                    currency='usd',
                    metadata={
                        'order_id': order.id,
                        'user_id': request.user.id
                    }
                )
                
                return Response({
                    'client_secret': intent.client_secret,
                    'payment_intent_id': intent.id,
                    'amount': order.total_amount
                })
                
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
            except stripe.error.StripeError as e:
                return Response(
                    {'error': f"Stripe error: {str(e)}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CODPaymentView(generics.CreateAPIView):
    """
    View for Cash on Delivery payments.
    """
    serializer_class = CODPaymentSerializer
    permission_classes = [IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create COD payment."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            try:
                order_id = serializer.validated_data['order_id']
                order = Order.objects.get(id=order_id, user=request.user)
                
                # Create COD payment
                payment = Payment.objects.create(
                    order=order,
                    provider='cod',
                    amount=order.total_amount,
                    currency=order.currency,
                    status='pending',
                    payment_type='payment'
                )
                
                # Update order status
                order.payment_status = 'pending'
                order.status = 'confirmed'
                order.save()
                
                response_serializer = PaymentDetailSerializer(
                    payment,
                    context={'request': request}
                )
                return Response(response_serializer.data, status=status.HTTP_201_CREATED)
                
            except Order.DoesNotExist:
                return Response(
                    {'error': 'Order not found'},
                    status=status.HTTP_404_NOT_FOUND
                )
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PaymentWebhookView(generics.CreateAPIView):
    """
    View for handling payment webhooks (Stripe).
    """
    permission_classes = []  # No authentication required for webhooks
    
    def post(self, request, *args, **kwargs):
        """Handle Stripe webhook."""
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')
        endpoint_secret = settings.STRIPE_WEBHOOK_SECRET
        
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, endpoint_secret
            )
        except ValueError:
            return Response(
                {'error': 'Invalid payload'},
                status=status.HTTP_400_BAD_REQUEST
            )
        except stripe.error.SignatureVerificationError:
            return Response(
                {'error': 'Invalid signature'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create webhook record
        webhook = PaymentWebhook.objects.create(
            provider='stripe',
            provider_webhook_id=event.get('id', ''),
            event_type=event['type'],
            event_data=event['data'],
            status='pending'
        )
        
        # Process webhook
        try:
            self._process_stripe_webhook(event, webhook)
            webhook.status = 'processed'
            webhook.processed_at = timezone.now()
        except Exception as e:
            webhook.status = 'failed'
            webhook.processing_notes = str(e)
        
        webhook.save()
        
        return Response({'status': 'success'})
    
    def _process_stripe_webhook(self, event, webhook):
        """Process Stripe webhook event."""
        if event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
            payment_id = payment_intent['metadata'].get('payment_id')
            
            if payment_id:
                try:
                    payment = Payment.objects.get(payment_id=payment_id)
                    payment.status = 'succeeded'
                    payment.processed_at = timezone.now()
                    payment.provider_payment_id = payment_intent['id']
                    payment.save()
                    
                    webhook.related_payment = payment
                except Payment.DoesNotExist:
                    pass
        
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
            payment_id = payment_intent['metadata'].get('payment_id')
            
            if payment_id:
                try:
                    payment = Payment.objects.get(payment_id=payment_id)
                    payment.status = 'failed'
                    payment.failure_reason = payment_intent.get('last_payment_error', {}).get('message', 'Payment failed')
                    payment.save()
                    
                    webhook.related_payment = payment
                except Payment.DoesNotExist:
                    pass


class PaymentReportView(generics.GenericAPIView):
    """
    View for generating payment reports.
    """
    serializer_class = PaymentReportSerializer
    permission_classes = [IsStaffOrAdmin]
    
    def post(self, request):
        """Generate payment report."""
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            date_from = serializer.validated_data['date_from']
            date_to = serializer.validated_data['date_to']
            provider = serializer.validated_data.get('provider')
            status_filter = serializer.validated_data.get('status')
            
            # Build query
            payments = Payment.objects.filter(
                created_at__date__gte=date_from,
                created_at__date__lte=date_to
            )
            
            if provider:
                payments = payments.filter(provider=provider)
            if status_filter:
                payments = payments.filter(status=status_filter)
            
            # Generate report data
            from django.db.models import Sum, Count, Avg
            
            report_data = {
                'period': f"{date_from} to {date_to}",
                'total_payments': payments.count(),
                'total_amount': payments.aggregate(Sum('amount'))['amount__sum'] or Decimal('0.00'),
                'average_amount': payments.aggregate(Avg('amount'))['amount__avg'] or Decimal('0.00'),
                'by_status': payments.values('status').annotate(
                    count=Count('id'),
                    total=Sum('amount')
                ),
                'by_provider': payments.values('provider').annotate(
                    count=Count('id'),
                    total=Sum('amount')
                ),
                'payments': PaymentListSerializer(
                    payments[:100],  # Limit to 100 for performance
                    many=True,
                    context={'request': request}
                ).data
            }
            
            return Response(report_data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
