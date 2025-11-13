import logging
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from .models import NewsletterSubscriber, Newsletter, NewsletterSendLog

logger = logging.getLogger(__name__)


class NewsletterEmailService:
    """Service for sending newsletter emails"""
    
    @staticmethod
    def send_welcome_email(subscriber):
        """Send welcome email to new subscriber"""
        try:
            subject = "Welcome to Unique & Antique Newsletter!"
            
            # HTML content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Our Newsletter</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .button {{ display: inline-block; background: #10b981; color: white; padding: 12px 30px; text-decoration: none; border-radius: 5px; margin: 20px 0; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to Unique & Antique!</h1>
                        <p>Thank you for subscribing to our newsletter</p>
                    </div>
                    <div class="content">
                        <h2>Hello{' ' + subscriber.name if subscriber.name else ''}!</h2>
                        <p>We're thrilled to have you join our community of antique and unique item enthusiasts!</p>
                        
                        <p>As a subscriber, you'll receive:</p>
                        <ul>
                            <li>🏺 Latest antique arrivals and rare finds</li>
                            <li>💰 Exclusive discounts and early access to sales</li>
                            <li>📚 Expert tips on collecting and caring for antiques</li>
                            <li>🎯 Personalized recommendations based on your interests</li>
                        </ul>
                        
                        <p>Start exploring our collection of unique treasures:</p>
                        <a href="http://localhost:3000/products" class="button">Browse Our Collection</a>
                        
                        <p>If you have any questions, feel free to reach out to us anytime.</p>
                        
                        <p>Happy collecting!<br>
                        The Unique & Antique Team</p>
                    </div>
                    <div class="footer">
                        <p>You're receiving this email because you subscribed to our newsletter.</p>
                        <p>If you no longer wish to receive these emails, you can unsubscribe at any time.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_content = strip_tags(html_content)
            
            # Send email
            success = send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[subscriber.email],
                html_message=html_content,
                fail_silently=False
            )
            
            logger.info(f"Welcome email sent to {subscriber.email}: {success}")
            return success
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {subscriber.email}: {str(e)}")
            return False
    
    @staticmethod
    def send_newsletter(newsletter):
        """Send newsletter to all active subscribers"""
        try:
            # Get all active subscribers
            subscribers = NewsletterSubscriber.objects.filter(is_active=True)
            newsletter.recipients_count = subscribers.count()
            
            if newsletter.recipients_count == 0:
                return {
                    'success': False,
                    'error': 'No active subscribers found',
                    'sent_count': 0,
                    'failed_count': 0
                }
            
            sent_count = 0
            failed_count = 0
            
            # Prepare email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>{newsletter.subject}</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>Unique & Antique</h1>
                        <h2>{newsletter.title}</h2>
                    </div>
                    <div class="content">
                        {newsletter.content}
                    </div>
                    <div class="footer">
                        <p>You're receiving this email because you subscribed to our newsletter.</p>
                        <p>Visit our store: <a href="http://localhost:3000">Unique & Antique</a></p>
                        <p>If you no longer wish to receive these emails, you can unsubscribe at any time.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_content = strip_tags(html_content)
            
            # Send to each subscriber
            for subscriber in subscribers:
                try:
                    success = send_mail(
                        subject=newsletter.subject,
                        message=plain_content,
                        from_email=settings.DEFAULT_FROM_EMAIL,
                        recipient_list=[subscriber.email],
                        html_message=html_content,
                        fail_silently=False
                    )
                    
                    if success:
                        sent_count += 1
                        # Log successful send
                        NewsletterSendLog.objects.create(
                            newsletter=newsletter,
                            subscriber=subscriber,
                            success=True
                        )
                    else:
                        failed_count += 1
                        # Log failed send
                        NewsletterSendLog.objects.create(
                            newsletter=newsletter,
                            subscriber=subscriber,
                            success=False,
                            error_message="Email sending failed"
                        )
                        
                except Exception as e:
                    failed_count += 1
                    logger.error(f"Failed to send newsletter to {subscriber.email}: {str(e)}")
                    # Log failed send
                    NewsletterSendLog.objects.create(
                        newsletter=newsletter,
                        subscriber=subscriber,
                        success=False,
                        error_message=str(e)
                    )
            
            # Update newsletter status
            newsletter.status = Newsletter.SENT
            newsletter.sent_at = timezone.now()
            newsletter.sent_count = sent_count
            newsletter.failed_count = failed_count
            newsletter.save()
            
            logger.info(f"Newsletter '{newsletter.title}' sent: {sent_count} success, {failed_count} failed")
            
            return {
                'success': True,
                'sent_count': sent_count,
                'failed_count': failed_count
            }
            
        except Exception as e:
            logger.error(f"Error sending newsletter '{newsletter.title}': {str(e)}")
            return {
                'success': False,
                'error': str(e),
                'sent_count': 0,
                'failed_count': 0
            }
