import logging
import secrets
import random
from datetime import datetime, timedelta
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.cache import cache

User = get_user_model()
logger = logging.getLogger(__name__)


class PasswordResetService:
    """Service for handling password reset functionality"""
    
    @staticmethod
    def send_password_reset_email(email):
        """Send password reset email with 6-digit code to user"""
        try:
            # Check if user exists
            try:
                user = User.objects.get(email=email, is_active=True)
            except User.DoesNotExist:
                # Don't reveal if email exists or not for security
                logger.warning(f"Password reset requested for non-existent email: {email}")
                return {
                    'success': True,  # Always return success for security
                    'message': 'If an account with this email exists, you will receive a password reset code.'
                }
            
            # Generate 6-digit code
            reset_code = str(random.randint(100000, 999999))
            
            # Store code in cache with 15-minute expiration
            cache_key = f"password_reset_{email}"
            cache.set(cache_key, {
                'code': reset_code,
                'user_id': user.id,
                'timestamp': timezone.now().isoformat()
            }, timeout=900)  # 15 minutes
            
            # Email subject
            subject = "Reset Your Password - Unique & Antique"
            
            # HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset Code</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1f2937, #374151); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .code-box {{ background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0; }}
                    .code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; font-family: monospace; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .warning {{ background: #fef3cd; border: 1px solid #fecaca; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🔐 Password Reset Code</h1>
                        <p>Unique & Antique Account Security</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user.first_name or user.username}!</h2>
                        <p>We received a request to reset the password for your Unique & Antique account.</p>
                        
                        <p>Use the following 6-digit code to reset your password:</p>
                        
                        <div class="code-box">
                            <div class="code">{reset_code}</div>
                        </div>
                        
                        <div class="warning">
                            <strong>⚠️ Security Notice:</strong>
                            <ul>
                                <li>This code will expire in 15 minutes for security reasons</li>
                                <li>If you didn't request this reset, please ignore this email</li>
                                <li>Your password will remain unchanged until you create a new one</li>
                                <li>Never share this code with anyone</li>
                            </ul>
                        </div>
                        
                        <p>Enter this code on the password reset page to continue with resetting your password.</p>
                        
                        <p>If you have any questions or concerns, please contact our support team.</p>
                        
                        <p>Best regards,<br>
                        The Unique & Antique Security Team</p>
                    </div>
                    <div class="footer">
                        <p>This email was sent because a password reset was requested for your account.</p>
                        <p>If you didn't request this, please secure your account and contact support.</p>
                        <p>© 2024 Unique & Antique. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_content = f"""
            Password Reset Code - Unique & Antique
            
            Hello {user.first_name or user.username}!
            
            We received a request to reset the password for your Unique & Antique account.
            
            Your 6-digit password reset code is: {reset_code}
            
            Security Notice:
            - This code will expire in 15 minutes for security reasons
            - If you didn't request this reset, please ignore this email
            - Your password will remain unchanged until you create a new one
            - Never share this code with anyone
            
            Enter this code on the password reset page to continue with resetting your password.
            
            If you have any questions or concerns, please contact our support team.
            
            Best regards,
            The Unique & Antique Security Team
            
            This email was sent because a password reset was requested for your account.
            If you didn't request this, please secure your account and contact support.
            """
            
            # Send email
            success = send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                html_message=html_content,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Password reset code sent successfully to {email}")
                return {
                    'success': True,
                    'message': 'If an account with this email exists, you will receive a 6-digit password reset code.'
                }
            else:
                logger.error(f"Failed to send password reset email to {email}")
                return {
                    'success': False,
                    'message': 'Failed to send password reset email. Please try again.'
                }
                
        except Exception as e:
            logger.error(f"Exception while sending password reset email to {email}: {str(e)}")
            return {
                'success': False,
                'message': 'An error occurred while processing your request. Please try again.'
            }
    
    @staticmethod
    def verify_reset_code(email, code):
        """Verify password reset code"""
        try:
            # Check cache for stored code
            cache_key = f"password_reset_{email}"
            cached_data = cache.get(cache_key)
            
            if not cached_data:
                return {'success': False, 'error': 'Invalid or expired reset code'}
            
            # Verify code matches
            if cached_data['code'] != code:
                return {'success': False, 'error': 'Invalid reset code'}
            
            # Get user
            try:
                user = User.objects.get(id=cached_data['user_id'], is_active=True)
                return {'success': True, 'user': user}
            except User.DoesNotExist:
                return {'success': False, 'error': 'User not found'}
                
        except Exception as e:
            logger.error(f"Exception during code verification: {str(e)}")
            return {'success': False, 'error': 'Verification failed'}
    
    @staticmethod
    def reset_password(email, code, new_password):
        """Reset user password with code verification"""
        try:
            # Verify code first
            verification = PasswordResetService.verify_reset_code(email, code)
            if not verification['success']:
                return verification
            
            user = verification['user']
            
            # Set new password
            user.set_password(new_password)
            user.save()
            
            # Clear the reset code from cache
            cache_key = f"password_reset_{email}"
            cache.delete(cache_key)
            
            # Send confirmation email
            PasswordResetService.send_password_reset_confirmation(user)
            
            logger.info(f"Password reset successful for user {user.email}")
            return {
                'success': True,
                'message': 'Your password has been reset successfully. You can now log in with your new password.'
            }
            
        except Exception as e:
            logger.error(f"Exception during password reset: {str(e)}")
            return {
                'success': False,
                'error': 'An error occurred while resetting your password. Please try again.'
            }
    
    @staticmethod
    def send_password_reset_confirmation(user):
        """Send confirmation email after successful password reset"""
        try:
            subject = "Password Reset Successful - Unique & Antique"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Password Reset Successful</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .success {{ background: #d1fae5; border: 1px solid #10b981; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>✅ Password Reset Successful</h1>
                        <p>Your account is now secure</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user.first_name or user.username}!</h2>
                        
                        <div class="success">
                            <strong>✅ Success!</strong> Your password has been reset successfully.
                        </div>
                        
                        <p>Your Unique & Antique account password has been changed. You can now log in using your new password.</p>
                        
                        <p><strong>What's next?</strong></p>
                        <ul>
                            <li>Log in to your account with your new password</li>
                            <li>Consider enabling two-factor authentication for extra security</li>
                            <li>Make sure to use a strong, unique password</li>
                        </ul>
                        
                        <p><strong>⚠️ If you didn't reset your password:</strong></p>
                        <p>If you didn't request this password reset, please contact our support team immediately as your account may have been compromised.</p>
                        
                        <p>Thank you for keeping your account secure!</p>
                        
                        <p>Best regards,<br>
                        The Unique & Antique Security Team</p>
                    </div>
                    <div class="footer">
                        <p>This is a security notification for your Unique & Antique account.</p>
                        <p>© 2024 Unique & Antique. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
            Password Reset Successful - Unique & Antique
            
            Hello {user.first_name or user.username}!
            
            Your Unique & Antique account password has been changed successfully.
            You can now log in using your new password.
            
            What's next?
            - Log in to your account with your new password
            - Consider enabling two-factor authentication for extra security
            - Make sure to use a strong, unique password
            
            If you didn't reset your password:
            If you didn't request this password reset, please contact our support team 
            immediately as your account may have been compromised.
            
            Thank you for keeping your account secure!
            
            Best regards,
            The Unique & Antique Security Team
            """
            
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=True  # Don't fail the reset if confirmation email fails
            )
            
            logger.info(f"Password reset confirmation sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Failed to send password reset confirmation to {user.email}: {str(e)}")


class EmailVerificationService:
    """Service for handling email verification functionality"""
    
    @staticmethod
    def send_verification_email(user):
        """Send email verification code to user"""
        try:
            # Generate 6-digit code
            verification_code = str(random.randint(100000, 999999))
            
            # Store code in cache with 30-minute expiration
            cache_key = f"email_verification_{user.email}"
            cache.set(cache_key, {
                'code': verification_code,
                'user_id': user.id,
                'timestamp': timezone.now().isoformat()
            }, timeout=1800)  # 30 minutes
            
            # Email subject
            subject = "Verify Your Email - Unique & Antique"
            
            # HTML email content
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Email Verification</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #1f2937, #374151); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .code-box {{ background: #1f2937; color: white; padding: 20px; text-align: center; border-radius: 8px; margin: 20px 0; }}
                    .code {{ font-size: 32px; font-weight: bold; letter-spacing: 8px; font-family: monospace; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .warning {{ background: #dbeafe; border: 1px solid #3b82f6; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to Unique & Antique!</h1>
                        <p>Verify Your Email Address</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user.first_name or user.username}!</h2>
                        <p>Thank you for joining Unique & Antique! To complete your registration and start exploring our amazing collection of antiques and unique items, please verify your email address.</p>
                        
                        <p>Use the following 6-digit code to verify your email:</p>
                        
                        <div class="code-box">
                            <div class="code">{verification_code}</div>
                        </div>
                        
                        <div class="warning">
                            <strong>📋 Verification Instructions:</strong>
                            <ul>
                                <li>This code will expire in 30 minutes</li>
                                <li>Enter this code on the verification page</li>
                                <li>Once verified, you can access all features</li>
                                <li>Keep this code secure and don't share it</li>
                            </ul>
                        </div>
                        
                        <p>After verification, you'll be able to:</p>
                        <ul>
                            <li>Browse our exclusive collection of antiques</li>
                            <li>Add items to your wishlist and cart</li>
                            <li>Place orders and track shipments</li>
                            <li>Leave reviews and ratings</li>
                            <li>Receive personalized recommendations</li>
                        </ul>
                        
                        <p>If you didn't create this account, please ignore this email.</p>
                        
                        <p>Welcome aboard!<br>
                        The Unique & Antique Team</p>
                    </div>
                    <div class="footer">
                        <p>This email was sent to verify your account registration.</p>
                        <p>© 2024 Unique & Antique. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            # Plain text version
            plain_content = f"""
            Welcome to Unique & Antique!
            
            Hello {user.first_name or user.username}!
            
            Thank you for joining Unique & Antique! To complete your registration, please verify your email address.
            
            Your 6-digit verification code is: {verification_code}
            
            Verification Instructions:
            - This code will expire in 30 minutes
            - Enter this code on the verification page
            - Once verified, you can access all features
            - Keep this code secure and don't share it
            
            After verification, you'll be able to browse our exclusive collection, add items to your wishlist, place orders, and much more!
            
            If you didn't create this account, please ignore this email.
            
            Welcome aboard!
            The Unique & Antique Team
            """
            
            # Send email
            success = send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=False
            )
            
            if success:
                logger.info(f"Email verification code sent successfully to {user.email}")
                return {
                    'success': True,
                    'message': 'Verification code sent to your email address.'
                }
            else:
                logger.error(f"Failed to send verification email to {user.email}")
                return {
                    'success': False,
                    'message': 'Failed to send verification email. Please try again.'
                }
                
        except Exception as e:
            logger.error(f"Exception while sending verification email to {user.email}: {str(e)}")
            return {
                'success': False,
                'message': 'An error occurred while sending verification email. Please try again.'
            }
    
    @staticmethod
    def verify_email_code(email, code):
        """Verify email verification code"""
        try:
            # Check cache for stored code
            cache_key = f"email_verification_{email}"
            cached_data = cache.get(cache_key)
            
            if not cached_data:
                return {'success': False, 'error': 'Invalid or expired verification code'}
            
            # Verify code matches
            if cached_data['code'] != code:
                return {'success': False, 'error': 'Invalid verification code'}
            
            # Get user and verify email
            try:
                user = User.objects.get(id=cached_data['user_id'])
                user.is_verified = True
                user.save()
                
                # Clear the verification code from cache
                cache.delete(cache_key)
                
                # Send welcome email
                EmailVerificationService.send_welcome_email(user)
                
                logger.info(f"Email verification successful for user {user.email}")
                return {
                    'success': True,
                    'message': 'Email verified successfully! Welcome to Unique & Antique.',
                    'user': user
                }
            except User.DoesNotExist:
                return {'success': False, 'error': 'User not found'}
                
        except Exception as e:
            logger.error(f"Exception during email verification: {str(e)}")
            return {'success': False, 'error': 'Verification failed'}
    
    @staticmethod
    def resend_verification_code(email):
        """Resend verification code to user"""
        try:
            user = User.objects.get(email=email, is_active=True)
            
            if user.is_verified:
                return {
                    'success': False,
                    'error': 'Email is already verified.'
                }
            
            return EmailVerificationService.send_verification_email(user)
            
        except User.DoesNotExist:
            return {
                'success': False,
                'error': 'User not found.'
            }
        except Exception as e:
            logger.error(f"Exception while resending verification code: {str(e)}")
            return {
                'success': False,
                'error': 'Failed to resend verification code.'
            }
    
    @staticmethod
    def send_welcome_email(user):
        """Send welcome email after successful verification"""
        try:
            subject = "Welcome to Unique & Antique! 🎉"
            
            html_content = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="utf-8">
                <title>Welcome to Unique & Antique</title>
                <style>
                    body {{ font-family: Arial, sans-serif; line-height: 1.6; color: #333; }}
                    .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                    .header {{ background: linear-gradient(135deg, #10b981, #059669); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                    .content {{ background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }}
                    .footer {{ text-align: center; margin-top: 30px; color: #666; font-size: 14px; }}
                    .feature-box {{ background: #f0fdf4; border: 1px solid #10b981; padding: 15px; border-radius: 5px; margin: 20px 0; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🎉 Welcome to Unique & Antique!</h1>
                        <p>Your account is now verified and ready to use</p>
                    </div>
                    <div class="content">
                        <h2>Hello {user.first_name or user.username}!</h2>
                        
                        <p>Congratulations! Your email has been successfully verified. You now have full access to all Unique & Antique features.</p>
                        
                        <div class="feature-box">
                            <strong>🛍️ What you can do now:</strong>
                            <ul>
                                <li>Explore our curated collection of antiques and unique items</li>
                                <li>Add items to your wishlist and shopping cart</li>
                                <li>Place orders with secure payment processing</li>
                                <li>Track your orders and shipments</li>
                                <li>Leave reviews and ratings for products</li>
                                <li>Receive personalized recommendations</li>
                                <li>Subscribe to our newsletter for exclusive deals</li>
                            </ul>
                        </div>
                        
                        <p>Ready to start your treasure hunting journey? Visit our website and discover amazing antiques from around the world!</p>
                        
                        <p>If you have any questions, our support team is here to help.</p>
                        
                        <p>Happy shopping!<br>
                        The Unique & Antique Team</p>
                    </div>
                    <div class="footer">
                        <p>Thank you for choosing Unique & Antique for your antique and collectible needs.</p>
                        <p>© 2024 Unique & Antique. All rights reserved.</p>
                    </div>
                </div>
            </body>
            </html>
            """
            
            plain_content = f"""
            Welcome to Unique & Antique!
            
            Hello {user.first_name or user.username}!
            
            Congratulations! Your email has been successfully verified. You now have full access to all Unique & Antique features.
            
            What you can do now:
            - Explore our curated collection of antiques and unique items
            - Add items to your wishlist and shopping cart
            - Place orders with secure payment processing
            - Track your orders and shipments
            - Leave reviews and ratings for products
            - Receive personalized recommendations
            - Subscribe to our newsletter for exclusive deals
            
            Ready to start your treasure hunting journey? Visit our website and discover amazing antiques from around the world!
            
            Happy shopping!
            The Unique & Antique Team
            """
            
            send_mail(
                subject=subject,
                message=plain_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_content,
                fail_silently=True  # Don't fail verification if welcome email fails
            )
            
            logger.info(f"Welcome email sent to {user.email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
