"""
Order email notification service for the Unique and Antique E-commerce Platform.
"""

from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import models
from decimal import Decimal
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class OrderEmailService:
    """Service for handling order-related email notifications"""
    
    @staticmethod
    def send_order_confirmation_email(order):
        """Send order confirmation email to customer and admin"""
        try:
            # Send to customer
            customer_result = OrderEmailService._send_customer_order_confirmation(order)
            
            # Send to admin
            admin_result = OrderEmailService._send_admin_order_notification(order, 'placed')
            
            return {
                'customer_email_sent': customer_result,
                'admin_email_sent': admin_result,
                'message': 'Order confirmation emails sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to send order confirmation emails for order {order.order_number}: {str(e)}")
            return {
                'customer_email_sent': False,
                'admin_email_sent': False,
                'error': str(e)
            }
    
    @staticmethod
    def send_order_status_change_email(order, old_status, new_status, changed_by=None):
        """Send order status change email to customer and admin"""
        try:
            # Send to customer
            customer_result = OrderEmailService._send_customer_status_update(order, old_status, new_status)
            
            # Send to admin
            admin_result = OrderEmailService._send_admin_status_notification(order, old_status, new_status, changed_by)
            
            return {
                'customer_email_sent': customer_result,
                'admin_email_sent': admin_result,
                'message': f'Order status change emails sent for {old_status} -> {new_status}'
            }
            
        except Exception as e:
            logger.error(f"Failed to send status change emails for order {order.order_number}: {str(e)}")
            return {
                'customer_email_sent': False,
                'admin_email_sent': False,
                'error': str(e)
            }
    
    @staticmethod
    def _send_customer_order_confirmation(order):
        """Send order confirmation email to customer"""
        try:
            subject = f"Order Confirmation - {order.order_number} | Unique & Antique"
            
            # Prepare context for email template
            context = {
                'order': order,
                'customer': order.user,
                'order_items': order.items.all(),
                'shipping_address': order.shipping_address,
                'billing_address': order.billing_address,
                'estimated_delivery': order.estimated_delivery_date,
                'total_items': order.total_items,
                'company_name': 'Unique & Antique',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'current_year': timezone.now().year,
            }
            
            # Render HTML email
            html_message = render_to_string('orders/emails/order_confirmation_customer.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/order_confirmation_customer.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Order confirmation email sent to customer {order.user.email} for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send customer order confirmation for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_admin_order_notification(order, action_type):
        """Send order notification email to admin"""
        try:
            admin_emails = OrderEmailService._get_admin_emails()
            if not admin_emails:
                logger.warning("No admin emails configured for order notifications")
                return False
            
            subject = f"New Order {action_type.title()} - {order.order_number} | Unique & Antique"
            
            # Prepare context for email template
            context = {
                'order': order,
                'customer': order.user,
                'order_items': order.items.all(),
                'action_type': action_type,
                'total_items': order.total_items,
                'company_name': 'Unique & Antique',
                'admin_url': f"{settings.FRONTEND_URL}/admin/orders/{order.id}/",
                'current_year': timezone.now().year,
            }
            
            # Render HTML email
            html_message = render_to_string('orders/emails/order_notification_admin.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/order_notification_admin.txt', context)
            
            # Send email to all admins
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Order {action_type} notification sent to admins for order {order.order_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin order notification for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_customer_status_update(order, old_status, new_status):
        """Send order status update email to customer"""
        try:
            # Get user-friendly status names
            status_display = dict(order.STATUS_CHOICES)
            old_status_display = status_display.get(old_status, old_status.title())
            new_status_display = status_display.get(new_status, new_status.title())
            
            subject = f"Order Update - {order.order_number} is now {new_status_display} | Unique & Antique"
            
            # Prepare context for email template
            context = {
                'order': order,
                'customer': order.user,
                'old_status': old_status,
                'new_status': new_status,
                'old_status_display': old_status_display,
                'new_status_display': new_status_display,
                'tracking_number': order.tracking_number,
                'carrier': order.carrier,
                'estimated_delivery': order.estimated_delivery_date,
                'company_name': 'Unique & Antique',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'order_url': f"{settings.FRONTEND_URL}/orders/{order.order_number}/",
                'current_year': timezone.now().year,
            }
            
            # Add status-specific information
            if new_status == 'confirmed':
                context['message'] = "Great news! Your order has been confirmed and is being prepared for shipment."
            elif new_status == 'shipped':
                context['message'] = "Your order is on its way! You can track your package using the tracking information below."
            elif new_status == 'delivered':
                context['message'] = "Your order has been delivered! We hope you love your unique antique items."
            elif new_status == 'cancelled':
                context['message'] = "Your order has been cancelled. If you have any questions, please contact our support team."
            elif new_status == 'returned':
                context['message'] = "Your return has been processed. Please allow 3-5 business days for the refund to appear in your account."
            else:
                context['message'] = f"Your order status has been updated to {new_status_display}."
            
            # Render HTML email
            html_message = render_to_string('orders/emails/order_status_update_customer.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/order_status_update_customer.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Status update email sent to customer {order.user.email} for order {order.order_number}: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send customer status update for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_admin_status_notification(order, old_status, new_status, changed_by=None):
        """Send order status change notification to admin"""
        try:
            admin_emails = OrderEmailService._get_admin_emails()
            if not admin_emails:
                logger.warning("No admin emails configured for status change notifications")
                return False
            
            # Get user-friendly status names
            status_display = dict(order.STATUS_CHOICES)
            old_status_display = status_display.get(old_status, old_status.title())
            new_status_display = status_display.get(new_status, new_status.title())
            
            subject = f"Order Status Changed - {order.order_number}: {old_status_display} → {new_status_display}"
            
            # Prepare context for email template
            context = {
                'order': order,
                'customer': order.user,
                'old_status': old_status,
                'new_status': new_status,
                'old_status_display': old_status_display,
                'new_status_display': new_status_display,
                'changed_by': changed_by,
                'change_time': timezone.now(),
                'company_name': 'Unique & Antique',
                'admin_url': f"{settings.FRONTEND_URL}/admin/orders/{order.id}/",
                'current_year': timezone.now().year,
            }
            
            # Render HTML email
            html_message = render_to_string('orders/emails/order_status_admin.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/order_status_admin.txt', context)
            
            # Send email to all admins
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Status change notification sent to admins for order {order.order_number}: {old_status} -> {new_status}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin status notification for order {order.order_number}: {str(e)}")
            return False
    
    @staticmethod
    def _get_admin_emails():
        """Get list of admin email addresses"""
        try:
            # Get all staff/admin users
            admin_users = User.objects.filter(
                models.Q(is_staff=True) | models.Q(is_superuser=True),
                is_active=True,
                email__isnull=False
            ).exclude(email='')
            
            admin_emails = [user.email for user in admin_users]
            
            # Add default admin email from settings if configured
            if hasattr(settings, 'ADMIN_EMAIL') and settings.ADMIN_EMAIL:
                if settings.ADMIN_EMAIL not in admin_emails:
                    admin_emails.append(settings.ADMIN_EMAIL)
            
            return admin_emails
            
        except Exception as e:
            logger.error(f"Failed to get admin emails: {str(e)}")
            return []
    
    @staticmethod
    def send_order_return_email(order_return):
        """Send order return notification emails"""
        try:
            # Send to customer
            customer_result = OrderEmailService._send_customer_return_confirmation(order_return)
            
            # Send to admin
            admin_result = OrderEmailService._send_admin_return_notification(order_return)
            
            return {
                'customer_email_sent': customer_result,
                'admin_email_sent': admin_result,
                'message': 'Order return emails sent successfully'
            }
            
        except Exception as e:
            logger.error(f"Failed to send order return emails for return {order_return.return_number}: {str(e)}")
            return {
                'customer_email_sent': False,
                'admin_email_sent': False,
                'error': str(e)
            }
    
    @staticmethod
    def _send_customer_return_confirmation(order_return):
        """Send return confirmation email to customer"""
        try:
            subject = f"Return Request Received - {order_return.return_number} | Unique & Antique"
            
            # Prepare context for email template
            context = {
                'order_return': order_return,
                'order': order_return.order,
                'customer': order_return.order.user,
                'return_items': order_return.items.all(),
                'reason_display': order_return.get_reason_display(),
                'company_name': 'Unique & Antique',
                'support_email': settings.DEFAULT_FROM_EMAIL,
                'current_year': timezone.now().year,
            }
            
            # Render HTML email
            html_message = render_to_string('orders/emails/return_confirmation_customer.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/return_confirmation_customer.txt', context)
            
            # Send email
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[order_return.order.user.email],
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Return confirmation email sent to customer for return {order_return.return_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send customer return confirmation for return {order_return.return_number}: {str(e)}")
            return False
    
    @staticmethod
    def _send_admin_return_notification(order_return):
        """Send return notification email to admin"""
        try:
            admin_emails = OrderEmailService._get_admin_emails()
            if not admin_emails:
                logger.warning("No admin emails configured for return notifications")
                return False
            
            subject = f"New Return Request - {order_return.return_number} | Unique & Antique"
            
            # Prepare context for email template
            context = {
                'order_return': order_return,
                'order': order_return.order,
                'customer': order_return.order.user,
                'return_items': order_return.items.all(),
                'reason_display': order_return.get_reason_display(),
                'company_name': 'Unique & Antique',
                'admin_url': f"{settings.FRONTEND_URL}/admin/returns/{order_return.id}/",
                'current_year': timezone.now().year,
            }
            
            # Render HTML email
            html_message = render_to_string('orders/emails/return_notification_admin.html', context)
            
            # Render plain text email
            plain_message = render_to_string('orders/emails/return_notification_admin.txt', context)
            
            # Send email to all admins
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=admin_emails,
                html_message=html_message,
                fail_silently=False
            )
            
            logger.info(f"Return notification sent to admins for return {order_return.return_number}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send admin return notification for return {order_return.return_number}: {str(e)}")
            return False
