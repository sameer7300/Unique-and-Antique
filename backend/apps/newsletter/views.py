import logging
from rest_framework import status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from .models import NewsletterSubscriber
from .serializers import NewsletterSubscriberSerializer, NewsletterUnsubscribeSerializer
from .services import NewsletterEmailService

logger = logging.getLogger(__name__)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def subscribe_newsletter(request):
    """
    Subscribe to newsletter
    """
    try:
        serializer = NewsletterSubscriberSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Newsletter subscription validation failed: {serializer.errors}")
            return Response(
                {
                    'error': 'Please check your form data and try again.',
                    'validation_errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Save the subscription with IP address
        subscriber = serializer.save(ip_address=get_client_ip(request))
        logger.info(f"Newsletter subscription created: {subscriber.email}")
        
        # Send welcome email (don't fail the request if email sending fails)
        email_sent = False
        try:
            email_sent = NewsletterEmailService.send_welcome_email(subscriber)
            if email_sent:
                logger.info(f"Welcome email sent to {subscriber.email}")
            else:
                logger.warning(f"Failed to send welcome email to {subscriber.email}")
        except Exception as e:
            logger.error(f"Exception while sending welcome email to {subscriber.email}: {str(e)}")
        
        return Response(
            {
                'message': 'Thank you for subscribing to our newsletter! Check your email for a welcome message.',
                'data': {
                    'email': subscriber.email,
                    'name': subscriber.name,
                    'subscribed_at': subscriber.subscribed_at
                },
                'email_sent': email_sent
            },
            status=status.HTTP_201_CREATED
        )
        
    except Exception as e:
        logger.error(f"Error creating newsletter subscription: {str(e)}")
        return Response(
            {
                'error': 'Failed to subscribe to newsletter. Please try again.',
                'details': str(e) if hasattr(request, 'user') and request.user.is_staff else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def unsubscribe_newsletter(request):
    """
    Unsubscribe from newsletter
    """
    try:
        serializer = NewsletterUnsubscribeSerializer(data=request.data)
        
        if not serializer.is_valid():
            logger.warning(f"Newsletter unsubscription validation failed: {serializer.errors}")
            return Response(
                {
                    'error': 'Please check your form data and try again.',
                    'validation_errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Unsubscribe the user
        subscriber = serializer.instance
        subscriber.unsubscribe()
        logger.info(f"Newsletter unsubscription: {subscriber.email}")
        
        return Response(
            {
                'message': 'You have been successfully unsubscribed from our newsletter.',
                'data': {
                    'email': subscriber.email,
                    'unsubscribed_at': subscriber.unsubscribed_at
                }
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error unsubscribing from newsletter: {str(e)}")
        return Response(
            {
                'error': 'Failed to unsubscribe from newsletter. Please try again.',
                'details': str(e) if hasattr(request, 'user') and request.user.is_staff else None
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def newsletter_stats(request):
    """
    Get newsletter statistics (public endpoint)
    """
    try:
        total_subscribers = NewsletterSubscriber.objects.filter(is_active=True).count()
        
        return Response(
            {
                'total_subscribers': total_subscribers,
                'message': f'Join {total_subscribers} other subscribers!'
            },
            status=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error getting newsletter stats: {str(e)}")
        return Response(
            {
                'error': 'Failed to get newsletter statistics.',
                'total_subscribers': 0
            },
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
