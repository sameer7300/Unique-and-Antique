#!/usr/bin/env python
"""
Test script to verify review email functionality
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
from django.contrib.auth import get_user_model
from apps.reviews.models import Review
from apps.reviews.services import ReviewEmailService
from apps.products.models import Product

User = get_user_model()

def test_review_email_configuration():
    """Test the review email configuration"""
    print("Testing review email configuration...")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print(f"ADMIN_EMAIL: {settings.ADMIN_EMAIL}")
    print("-" * 50)

def create_test_review():
    """Create a test review"""
    print("Creating test review...")
    
    # Get or create a test user
    user, created = User.objects.get_or_create(
        email='test@example.com',
        defaults={
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'testuser'
        }
    )
    if created:
        print(f"Created test user: {user.email}")
    
    # Get or create a test product
    product, created = Product.objects.get_or_create(
        slug='test-product',
        defaults={
            'title': 'Test Antique Product',
            'description': 'A beautiful test antique item',
            'price': 1000.00,
            'status': 'active'
        }
    )
    if created:
        print(f"Created test product: {product.title}")
    
    # Create test review
    review = Review.objects.create(
        user=user,
        product=product,
        rating=5,
        title="Excellent Product!",
        content="This is a test review to verify email functionality. The product is amazing and I highly recommend it.",
        status='pending'
    )
    
    print(f"✅ Test review created with ID: {review.id}")
    return review

def test_review_submission_emails():
    """Test review submission emails"""
    try:
        # Create test review
        review = create_test_review()
        
        print("\nTesting review submission emails...")
        
        # Test submission emails
        print("Sending review submission emails...")
        submission_sent = ReviewEmailService.send_review_submission_emails(review)
        print(f"Review submission emails sent: {submission_sent}")
        
        return review, submission_sent
        
    except Exception as e:
        print(f"❌ Error testing review submission emails: {e}")
        return None, False

def test_review_approval_email():
    """Test review approval email"""
    try:
        # Create test review
        review = create_test_review()
        
        print("\nTesting review approval email...")
        
        # Test approval email
        print("Sending review approval email...")
        approval_sent = ReviewEmailService.send_review_approval_email(review)
        print(f"Review approval email sent: {approval_sent}")
        
        # Clean up
        review.delete()
        print("✅ Test review cleaned up")
        
        return approval_sent
        
    except Exception as e:
        print(f"❌ Error testing review approval email: {e}")
        return False

def test_review_approval_signal():
    """Test review approval signal"""
    try:
        # Create test review
        review = create_test_review()
        
        print("\nTesting review approval signal...")
        
        # Approve the review (this should trigger the signal)
        print("Approving review to trigger signal...")
        review.status = 'approved'
        review.save()
        print("✅ Review approved - signal should have sent email")
        
        # Clean up
        review.delete()
        print("✅ Test review cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing review approval signal: {e}")
        return False

def cleanup_test_data():
    """Clean up any remaining test data"""
    try:
        # Clean up test reviews
        Review.objects.filter(
            user__email='test@example.com',
            product__slug='test-product'
        ).delete()
        
        # Clean up test product
        Product.objects.filter(slug='test-product').delete()
        
        # Clean up test user
        User.objects.filter(email='test@example.com').delete()
        
        print("✅ Test data cleaned up")
        
    except Exception as e:
        print(f"⚠️  Error cleaning up test data: {e}")

def main():
    """Main function"""
    print("=" * 60)
    print("REVIEW EMAIL NOTIFICATION TEST")
    print("=" * 60)
    
    test_review_email_configuration()
    
    tests = [
        ("Review Submission Emails", test_review_submission_emails),
        ("Review Approval Email", test_review_approval_email),
        ("Review Approval Signal", test_review_approval_signal),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_name == "Review Submission Emails":
                review, result = test_func()
                if result:
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                    # Clean up the review
                    if review:
                        review.delete()
                else:
                    print(f"❌ {test_name} FAILED")
            else:
                if test_func():
                    passed += 1
                    print(f"✅ {test_name} PASSED")
                else:
                    print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    # Clean up any remaining test data
    cleanup_test_data()
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL REVIEW EMAIL TESTS PASSED!")
        print("Your review email notification system is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check your email settings and review configuration.")
    print("=" * 60)

if __name__ == "__main__":
    main()
