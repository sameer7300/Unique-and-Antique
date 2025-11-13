"""
Contact email services for the Unique and Antique E-commerce Platform.
"""

from django.core.mail import send_mail, BadHeaderError
from django.template.loader import render_to_string
from django.conf import settings
from django.utils.html import strip_tags
import logging
import smtplib

logger = logging.getLogger(__name__)


class ContactEmailService:
    """
    Service class for handling contact form emails.
    """
    
    @staticmethod
    def send_contact_emails(contact_message):
        """
        Send emails to both admin and user when a contact form is submitted.
        """
        admin_sent = False
        user_sent = False
        
        try:
            # Send email to admin
            admin_sent = ContactEmailService._send_admin_notification(contact_message)
            logger.info(f"Admin notification sent: {admin_sent}")
            
        except Exception as e:
            logger.error(f"Failed to send admin notification: {str(e)}")
        
        try:
            # Send confirmation email to user
            user_sent = ContactEmailService._send_user_confirmation(contact_message)
            logger.info(f"User confirmation sent: {user_sent}")
            
        except Exception as e:
            logger.error(f"Failed to send user confirmation: {str(e)}")
        
        if admin_sent or user_sent:
            logger.info(f"Contact emails sent for message ID: {contact_message.id} (admin: {admin_sent}, user: {user_sent})")
            return True
        else:
            logger.error(f"Failed to send any emails for message ID: {contact_message.id}")
            return False
    
    @staticmethod
    def _send_admin_notification(contact_message):
        """
        Send notification email to admin about new contact message.
        """
        subject = f"New Contact Message: {contact_message.get_subject_display()}"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <h2 style="color: #2563eb; border-bottom: 2px solid #2563eb; padding-bottom: 10px;">
                    New Contact Message Received
                </h2>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Contact Details:</h3>
                    <p><strong>Name:</strong> {contact_message.name}</p>
                    <p><strong>Email:</strong> {contact_message.email}</p>
                    <p><strong>Subject:</strong> {contact_message.get_subject_display()}</p>
                    <p><strong>Date:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                </div>
                
                <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #2563eb; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Message:</h3>
                    <p style="white-space: pre-wrap;">{contact_message.message}</p>
                </div>
                
                <div style="margin-top: 30px; padding: 15px; background-color: #ecfdf5; border-radius: 8px;">
                    <p style="margin: 0; color: #065f46;">
                        <strong>Action Required:</strong> Please respond to this inquiry within 24 hours.
                    </p>
                </div>
                
                <hr style="margin: 30px 0; border: none; border-top: 1px solid #e5e7eb;">
                <p style="font-size: 12px; color: #6b7280;">
                    This email was automatically generated from the Unique & Antique contact form.
                </p>
            </div>
        </body>
        </html>
        """
        
        # Create plain text version
        plain_content = f"""
New Contact Message Received

Contact Details:
Name: {contact_message.name}
Email: {contact_message.email}
Subject: {contact_message.get_subject_display()}
Date: {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}

Message:
{contact_message.message}

Action Required: Please respond to this inquiry within 24 hours.

---
This email was automatically generated from the Unique & Antique contact form.
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
    def _send_user_confirmation(contact_message):
        """
        Send confirmation email to user who submitted the contact form.
        """
        subject = "Thank you for contacting Unique & Antique"
        
        # Create HTML content
        html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: center; margin-bottom: 30px;">
                    <h1 style="color: #2563eb; margin: 0;">Unique & Antique</h1>
                    <p style="color: #6b7280; margin: 5px 0;">Premium Products, Exceptional Service</p>
                </div>
                
                <h2 style="color: #1e40af;">Thank You for Contacting Us!</h2>
                
                <p>Dear {contact_message.name},</p>
                
                <p>We have received your message and appreciate you taking the time to contact us. 
                Our team is committed to providing excellent customer service and will respond to your inquiry as soon as possible.</p>
                
                <div style="background-color: #f8fafc; padding: 20px; border-radius: 8px; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #1e40af;">Your Message Details:</h3>
                    <p><strong>Subject:</strong> {contact_message.get_subject_display()}</p>
                    <p><strong>Date Submitted:</strong> {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}</p>
                    <p><strong>Reference ID:</strong> #{contact_message.id}</p>
                </div>
                
                <div style="background-color: #ffffff; padding: 20px; border-left: 4px solid #10b981; margin: 20px 0;">
                    <h3 style="margin-top: 0; color: #059669;">What Happens Next?</h3>
                    <ul style="margin: 0; padding-left: 20px;">
                        <li>Our customer service team will review your message</li>
                        <li>You can expect a response within 24 hours during business days</li>
                        <li>We'll contact you at the email address you provided</li>
                        <li>For urgent matters, you can also call us at +92 300 1234567</li>
                    </ul>
                </div>
                
                <div style="margin-top: 30px; padding: 20px; background-color: #fef3c7; border-radius: 8px;">
                    <h3 style="margin-top: 0; color: #92400e;">Need Immediate Assistance?</h3>
                    <p style="margin-bottom: 10px;">For urgent inquiries, you can reach us through:</p>
                    <p style="margin: 5px 0;"><strong>Phone:</strong> +92 300 1234567</p>
                    <p style="margin: 5px 0;"><strong>Email:</strong> support@uniqueandantique.pk</p>
                    <p style="margin: 5px 0;"><strong>Business Hours:</strong> Monday - Saturday, 9 AM - 6 PM PKT</p>
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
Thank You for Contacting Unique & Antique!

Dear {contact_message.name},

We have received your message and appreciate you taking the time to contact us. 
Our team is committed to providing excellent customer service and will respond to your inquiry as soon as possible.

Your Message Details:
Subject: {contact_message.get_subject_display()}
Date Submitted: {contact_message.created_at.strftime('%B %d, %Y at %I:%M %p')}
Reference ID: #{contact_message.id}

What Happens Next?
- Our customer service team will review your message
- You can expect a response within 24 hours during business days
- We'll contact you at the email address you provided
- For urgent matters, you can also call us at +92 300 1234567

Need Immediate Assistance?
Phone: +92 300 1234567
Email: support@uniqueandantique.pk
Business Hours: Monday - Saturday, 9 AM - 6 PM PKT

Thank you for choosing Unique & Antique

---
This is an automated confirmation email. Please do not reply to this message.
        """
        
        try:
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[contact_message.email],
                html_message=html_content,
                fail_silently=False,
            )
            return True
        except (BadHeaderError, smtplib.SMTPException, ConnectionError) as e:
            logger.error(f"Failed to send user confirmation email: {str(e)}")
            return False
