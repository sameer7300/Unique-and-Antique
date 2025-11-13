"""
Review email services for the Unique and Antique E-commerce Platform.
"""

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
import smtplib

logger = logging.getLogger(__name__)


class ReviewEmailService:
    """
    Service class for handling review-related emails.
    """
    
    @staticmethod
    def send_review_submission_emails(review):
        """
        Send emails to both admin and user when a review is submitted.
        """
        admin_sent = False
        user_sent = False
        
        try:
            # Send email to admin
            admin_sent = ReviewEmailService._send_admin_notification(review)
            logger.info(f"Admin notification sent: {admin_sent}")
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
        
        try:
            # Send confirmation email to user
            user_sent = ReviewEmailService._send_user_confirmation(review)
            logger.info(f"User confirmation sent: {user_sent}")
            
        except Exception as e:
            logger.error(f"Failed to send user confirmation: {str(e)}")
        
        if admin_sent or user_sent:
            logger.info(f"Review emails sent for review ID: {review.id} (admin: {admin_sent}, user: {user_sent})")
            return True
        else:
            logger.error(f"Failed to send any emails for review ID: {review.id}")
            return False
    
    @staticmethod
    def send_review_approval_email(review):
        """
        Send email to user when their review is approved.
        """
        try:
            user_sent = ReviewEmailService._send_approval_notification(review)
            logger.info(f"Review approval notification sent: {user_sent}")
            return user_sent
        except Exception as e:
            logger.error(f"Failed to send approval notification: {str(e)}")
            return False
    
    @staticmethod
    def _send_admin_notification(review):
        """
        Send notification email to admin about new review submission.
        """
        subject = f"New Review Submitted: {review.product.title}"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    New Product Review Submitted
                </h2>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Review Details:</h3>
                    <p><strong>Product:</strong> {review.product.title}</p>
                    <p><strong>Reviewer:</strong> {review.user.get_full_name()}</p>
                    <p><strong>Email:</strong> {review.user.email}</p>
                    <p><strong>Rating:</strong> {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)</p>
                    <p><strong>Title:</strong> {review.title}</p>
                    <p><strong>Verified Purchase:</strong> {'Yes' if review.is_verified_purchase else 'No'}</p>
                    <p><strong>Date:</strong> {review.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #2563eb; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Review Content:</h3>
                    <p style="white-space: pre-wrap;">{review.content}</p>
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #fef3c7; border-radius: 8px;">
                    <p style="margin: 0; color: #92400e;">
                        <strong>Action Required:</strong> Please review and moderate this review in the admin panel.
                    </p>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/admin/reviews/review/{review.id}/change/" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        Review in Admin Panel
                    </a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 12px; color: #6b7280;">
                    This email was automatically generated from the Unique & Antique review system.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_content = f"""
New Product Review Submitted

Review Details:
Product: {review.product.title}
Reviewer: {review.user.get_full_name()}
Email: {review.user.email}
Rating: {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)
Title: {review.title}
Verified Purchase: {'Yes' if review.is_verified_purchase else 'No'}
Date: {review.created_at.strftime('%B %d, %Y at %I:%M %p')}

Review Content:
{review.content}

Action Required: Please review and moderate this review in the admin panel.

---
This email was automatically generated from the Unique & Antique review system.
        """
        
        try:
            # Get admin email from settings
            admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@unique-antique.com')
            
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[admin_email],
                html_message=html_content,
                fail_silently=False,
            )
            logger.info(f"Admin notification email sent to: {admin_email}")
            return True
        except (BadHeaderError, smtplib.SMTPException, ConnectionError) as e:
            logger.error(f"Failed to send admin notification email: {str(e)}")
            return False
    
    @staticmethod
    def _send_user_confirmation(review):
        """
        Send confirmation email to user who submitted the review.
        """
        subject = "Thank you for your review - Unique & Antique"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin: 0;">Unique & Antique</h1>
                    <p style="color: #6b7280; margin: 5px 0;">Premium Products, Exceptional Service</p>
                </div>
                
                <h2 style="color: #1e40af;">Thank You for Your Review!</h2>
                
                <p>Dear {review.user.get_full_name()},</p>
                
                <p>We have received your review for <strong>{review.product.title}</strong> and truly appreciate you taking the time to share your experience with us and other customers.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Your Review Details:</h3>
                    <p><strong>Product:</strong> {review.product.title}</p>
                    <p><strong>Rating:</strong> {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)</p>
                    <p><strong>Title:</strong> {review.title}</p>
                    <p><strong>Date Submitted:</strong> {review.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Review ID:</strong> #{review.id}</p>
                </div>
                
                <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #10b981; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #059669;">What Happens Next?</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Our team will review your submission for quality and authenticity</li>
                        <li>Once approved, your review will be visible to other customers</li>
                        <li>You'll receive a notification email when your review is published</li>
                        <li>Your review helps other customers make informed decisions</li>
                    </ul>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #fef3c7; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #92400e;">Review Guidelines</h3>
                    <p style="margin-bottom: 10px;">To ensure the best experience for all customers, please note:</p>
                    <ul style="margin: 0; padding-left: 20px; color: #92400e;">
                        <li>Reviews should be honest and based on your actual experience</li>
                        <li>Please avoid inappropriate language or personal information</li>
                        <li>Focus on the product features, quality, and your experience</li>
                        <li>Reviews typically take 24-48 hours to be approved</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/products/{review.product.slug}" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                        View Product
                    </a>
                    <a href="{settings.FRONTEND_URL}/profile/reviews" 
                       style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        My Reviews
                    </a>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                
                <div style="text-align: center;">
                    <p style="color: #6b7280; margin-bottom: 10px;">Thank you for choosing Unique & Antique</p>
                    <p style="font-size: 12px; color: #9ca3af;">
                        This is an automated confirmation email. Please do not reply to this message.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_content = f"""
Thank You for Your Review - Unique & Antique!

Dear {review.user.get_full_name()},

We have received your review for {review.product.title} and truly appreciate you taking the time to share your experience with us and other customers.

Your Review Details:
Product: {review.product.title}
Rating: {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)
Title: {review.title}
Date Submitted: {review.created_at.strftime('%B %d, %Y at %I:%M %p')}
Review ID: #{review.id}

What Happens Next?
- Our team will review your submission for quality and authenticity
- Once approved, your review will be visible to other customers
- You'll receive a notification email when your review is published
- Your review helps other customers make informed decisions

Review Guidelines:
- Reviews should be honest and based on your actual experience
- Please avoid inappropriate language or personal information
- Focus on the product features, quality, and your experience
- Reviews typically take 24-48 hours to be approved

Thank you for choosing Unique & Antique

---
This is an automated confirmation email. Please do not reply to this message.
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[review.user.email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except (BadHeaderError, smtplib.SMTPException, ConnectionError) as e:
            logger.error(f"Failed to send user confirmation email: {str(e)}")
            return False
    
    @staticmethod
    def _send_approval_notification(review):
        """
        Send notification email to user when their review is approved.
        """
        subject = "Your review has been approved - Unique & Antique"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin: 0;">Unique & Antique</h1>
                    <p style="color: #6b7280; margin: 5px 0;">Premium Products, Exceptional Service</p>
                </div>
                
                <h2 style="color: #059669;">🎉 Your Review is Now Live!</h2>
                
                <p>Dear {review.user.get_full_name()},</p>
                
                <p>Great news! Your review for <strong>{review.product.title}</strong> has been approved and is now visible to other customers on our website.</p>
                
                <div style="background-color: #ecfdf5; padding: 20px; border-radius: 8px; margin: 20px 0; border-left: 4px solid #10b981;">
                    <h3 style="margin-top: 0; color: #059669;">Your Published Review:</h3>
                    <p><strong>Product:</strong> {review.product.title}</p>
                    <p><strong>Rating:</strong> {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)</p>
                    <p><strong>Title:</strong> {review.title}</p>
                    <p><strong>Published:</strong> {review.approved_at.strftime('%B %d, %Y at %I:%M %p') if review.approved_at else 'Just now'}</p>
                </div>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Thank You for Your Contribution!</h3>
                    <p>Your honest feedback helps other customers make informed purchasing decisions and helps us improve our products and services.</p>
                    <ul style="margin: 10px 0; padding-left: 20px;">
                        <li>Your review is now visible on the product page</li>
                        <li>Other customers can find your review helpful</li>
                        <li>You're contributing to our community of satisfied customers</li>
                    </ul>
                </div>
                
                <div style="text-align: center; margin: 30px 0;">
                    <a href="{settings.FRONTEND_URL}/products/{review.product.slug}#reviews" 
                       style="background-color: #2563eb; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block; margin-right: 10px;">
                        View Your Review
                    </a>
                    <a href="{settings.FRONTEND_URL}/profile/reviews" 
                       style="background-color: #10b981; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; display: inline-block;">
                        My Reviews
                    </a>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #fef3c7; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #92400e;">Keep Sharing Your Experience</h3>
                    <p style="margin-bottom: 10px;">We'd love to hear about your other purchases too!</p>
                    <p style="margin: 0; color: #92400e;">Your reviews help us maintain the quality and trust that Unique & Antique is known for.</p>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                
                <div style="text-align: center;">
                    <p style="color: #6b7280; margin-bottom: 10px;">Thank you for being a valued customer!</p>
                    <p style="font-size: 12px; color: #9ca3af;">
                        This is an automated notification email. Please do not reply to this message.
                    </p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_content = f"""
Your Review is Now Live! - Unique & Antique

Dear {review.user.get_full_name()},

Great news! Your review for {review.product.title} has been approved and is now visible to other customers on our website.

Your Published Review:
Product: {review.product.title}
Rating: {'★' * review.rating}{'☆' * (5 - review.rating)} ({review.rating}/5)
Title: {review.title}
Published: {review.approved_at.strftime('%B %d, %Y at %I:%M %p') if review.approved_at else 'Just now'}

Thank You for Your Contribution!
Your honest feedback helps other customers make informed purchasing decisions and helps us improve our products and services.

- Your review is now visible on the product page
- Other customers can find your review helpful
- You're contributing to our community of satisfied customers

Keep Sharing Your Experience:
We'd love to hear about your other purchases too! Your reviews help us maintain the quality and trust that Unique & Antique is known for.

Thank you for being a valued customer!

---
This is an automated notification email. Please do not reply to this message.
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[review.user.email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except (BadHeaderError, smtplib.SMTPException, ConnectionError) as e:
            logger.error(f"Failed to send approval notification email: {str(e)}")
            return False
