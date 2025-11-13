#!/usr/bin/env python
"""
Test script to verify email configuration with Hostinger SMTP
"""
import os
import sys
import django
from pathlib import Path

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import EmailMessage

def test_email_configuration():
    """Test the email configuration"""
    print("Testing email configuration...")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {settings.EMAIL_USE_TLS}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print("-" * 50)

def send_test_email():
    """Send a test email"""
    try:
        # Test 1: Simple send_mail
        print("Sending test email using send_mail...")
        send_mail(
            subject='Test Email from Unique & Antique',
            message='This is a test email to verify SMTP configuration with Hostinger.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        print("✅ Test email sent successfully using send_mail!")
        
        # Test 2: EmailMessage with HTML
        print("\nSending HTML test email using EmailMessage...")
        email = EmailMessage(
            subject='HTML Test Email from Unique & Antique',
            body="""
            <html>
                <body>
                    <h2 style="color: #10b981;">Unique & Antique Email Test</h2>
                    <p>This is a <strong>HTML test email</strong> to verify SMTP configuration.</p>
                    <p>Email settings:</p>
                    <ul>
                        <li>Host: {host}</li>
                        <li>Port: {port}</li>
                        <li>From: {from_email}</li>
                    </ul>
                    <p style="color: #059669;">If you receive this email, the configuration is working correctly!</p>
                </body>
            </html>
            """.format(
                host=settings.EMAIL_HOST,
                port=settings.EMAIL_PORT,
                from_email=settings.DEFAULT_FROM_EMAIL
            ),
            from_email=settings.DEFAULT_FROM_EMAIL,
            to=[settings.ADMIN_EMAIL],
        )
        email.content_subtype = "html"
        email.send()
        print("✅ HTML test email sent successfully using EmailMessage!")
        
        return True
        
    except Exception as e:
        print(f"❌ Error sending test email: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("UNIQUE & ANTIQUE - EMAIL CONFIGURATION TEST")
    print("=" * 60)
    
    test_email_configuration()
    
    print("\nAttempting to send test emails...")
    success = send_test_email()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 EMAIL CONFIGURATION TEST PASSED!")
        print("Your Hostinger email is configured correctly.")
    else:
        print("❌ EMAIL CONFIGURATION TEST FAILED!")
        print("Please check your email settings and credentials.")
    print("=" * 60)

if __name__ == "__main__":
    main()
