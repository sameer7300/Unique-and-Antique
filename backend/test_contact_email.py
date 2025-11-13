#!/usr/bin/env python
"""
Test script to verify contact form email functionality
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

from django.conf import settings
from apps.contact.models import ContactMessage
from apps.contact.services import ContactEmailService

def test_contact_email_configuration():
    """Test the contact email configuration"""
    print("Testing contact email configuration...")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print("-" * 50)

def create_test_contact_message():
    """Create a test contact message"""
    print("Creating test contact message...")
    
    contact_message = ContactMessage.objects.create(
        name="Test User",
        email="test@example.com",
        subject="general",
        message="This is a test message to verify contact form email functionality."
    )
    
    print(f"✅ Test contact message created with ID: {contact_message.id}")
    return contact_message

def test_contact_emails():
    """Test sending contact emails"""
    try:
        # Create test message
        contact_message = create_test_contact_message()
        
        print("\nTesting contact email sending...")
        
        # Test admin notification
        print("Sending admin notification...")
        admin_sent = ContactEmailService._send_admin_notification(contact_message)
        print(f"Admin notification sent: {admin_sent}")
        
        # Test user confirmation
        print("Sending user confirmation...")
        user_sent = ContactEmailService._send_user_confirmation(contact_message)
        print(f"User confirmation sent: {user_sent}")
        
        # Test combined function
        print("Testing combined email function...")
        both_sent = ContactEmailService.send_contact_emails(contact_message)
        print(f"Both emails sent: {both_sent}")
        
        # Clean up test message
        contact_message.delete()
        print("✅ Test message cleaned up")
        
        return admin_sent and user_sent
        
    except Exception as e:
        print(f"❌ Error testing contact emails: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("CONTACT FORM EMAIL TEST")
    print("=" * 60)
    
    test_contact_email_configuration()
    
    print("\nAttempting to test contact form emails...")
    success = test_contact_emails()
    
    print("\n" + "=" * 60)
    if success:
        print("🎉 CONTACT EMAIL TEST PASSED!")
        print("Both admin and user emails are working correctly.")
    else:
        print("❌ CONTACT EMAIL TEST FAILED!")
        print("Please check your email settings and credentials.")
    print("=" * 60)

if __name__ == "__main__":
    main()
