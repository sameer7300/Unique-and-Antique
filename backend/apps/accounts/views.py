"""
Views for the accounts app.
"""

import time
from rest_framework import status, permissions, generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    ProfileSerializer,
    UserSerializer,
    UserUpdateSerializer,
    AddressSerializer,
    ChangePasswordSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
    TwoFactorSetupSerializer,
    TwoFactorVerifySerializer,
    DeleteAccountSerializer
)
from .services import PasswordResetService, EmailVerificationService
import logging
import pyotp
import qrcode
import io
import base64

logger = logging.getLogger(__name__)
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.contrib.auth.tokens import default_token_generator

from .models import User, Profile, Address
from apps.orders.models import Order
from apps.reviews.models import Review


class UserRegistrationView(APIView):
    """
    User registration endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            # Send email verification code
            verification_result = EmailVerificationService.send_verification_email(user)
            
            if verification_result['success']:
                return Response({
                    'message': 'User registered successfully. Please check your email for verification code.',
                    'email': user.email,
                    'verification_required': True
                }, status=status.HTTP_201_CREATED)
            else:
                # If email sending fails, still allow registration but notify user
                return Response({
                    'message': 'User registered successfully, but verification email failed to send. Please try to resend verification.',
                    'email': user.email,
                    'verification_required': True,
                    'email_error': verification_result['message']
                }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    """
    User login endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Check if email is verified
            if not user.is_verified:
                # Automatically send verification email
                from .services import EmailVerificationService
                verification_result = EmailVerificationService.send_verification_email(user)
                
                if verification_result['success']:
                    return Response({
                        'error': 'Please verify your email address before logging in.',
                        'email': user.email,
                        'verification_required': True,
                        'message': 'Your account is not yet verified. We have sent a new verification code to your email.'
                    }, status=status.HTTP_403_FORBIDDEN)
                else:
                    return Response({
                        'error': 'Please verify your email address before logging in.',
                        'email': user.email,
                        'verification_required': True,
                        'message': 'Your account is not yet verified. Please check your email for the verification code or click resend.',
                        'email_error': verification_result['message']
                    }, status=status.HTTP_403_FORBIDDEN)
            
            # Check if 2FA is enabled for this user
            if user.two_factor_enabled:
                # Store user ID in session for 2FA verification
                request.session['pending_2fa_user_id'] = user.id
                request.session['pending_2fa_timestamp'] = int(time.time())
                
                return Response({
                    'message': '2FA verification required',
                    'requires_2fa': True,
                    'user_id': user.id,
                    'email': user.email
                }, status=status.HTTP_200_OK)
            
            # Complete login for users without 2FA
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token),
                }
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLogin2FAView(APIView):
    """
    Complete 2FA login endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        try:
            code = request.data.get('code')
            
            if not code:
                return Response({
                    'error': '2FA verification code is required.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get pending user from session
            user_id = request.session.get('pending_2fa_user_id')
            timestamp = request.session.get('pending_2fa_timestamp')
            
            if not user_id or not timestamp:
                return Response({
                    'error': 'No pending 2FA session found. Please login again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Check if session is expired (5 minutes timeout)
            current_time = int(time.time())
            if current_time - timestamp > 300:  # 5 minutes
                # Clear expired session
                request.session.pop('pending_2fa_user_id', None)
                request.session.pop('pending_2fa_timestamp', None)
                return Response({
                    'error': '2FA session expired. Please login again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Get user and verify 2FA code
            User = get_user_model()
            try:
                user = User.objects.get(id=user_id, two_factor_enabled=True)
            except User.DoesNotExist:
                return Response({
                    'error': 'Invalid 2FA session.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Verify 2FA code
            import pyotp
            totp = pyotp.TOTP(user.two_factor_secret)
            if not totp.verify(code, valid_window=1):
                return Response({
                    'error': 'Invalid 2FA code. Please try again.'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clear 2FA session
            request.session.pop('pending_2fa_user_id', None)
            request.session.pop('pending_2fa_timestamp', None)
            
            # Complete login
            login(request, user)
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'message': 'Login successful',
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token),
                }
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in 2FA login: {str(e)}")
            return Response({
                'error': 'An error occurred during 2FA verification.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class UserLogoutView(APIView):
    """
    User logout endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                token = RefreshToken(refresh_token)
                token.blacklist()
            
            logout(request)
            return Response({
                'message': 'Logout successful'
            }, status=status.HTTP_200_OK)
        
        except Exception as e:
            return Response({
                'error': 'Invalid token'
            }, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """
    User profile retrieve and update endpoint.
    """
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class UserUpdateView(generics.UpdateAPIView):
    """
    User information update endpoint.
    """
    serializer_class = UserUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user


class ProfileUpdateView(generics.RetrieveUpdateAPIView):
    """
    User profile update endpoint.
    """
    serializer_class = ProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile


class ChangePasswordView(APIView):
    """
    Change password endpoint.
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'message': 'Password changed successfully'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetView(APIView):
    """
    Password reset request endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        
        if serializer.is_valid():
            email = serializer.validated_data['email']
            user = User.objects.get(email=email)
            
            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))
            
            # Send password reset email
            reset_url = f"{settings.FRONTEND_URL}/reset-password/{uid}/{token}/"
            
            send_mail(
                subject='Password Reset Request',
                message=f'Click the link to reset your password: {reset_url}',
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'message': 'Password reset email sent'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PasswordResetConfirmView(APIView):
    """
    Password reset confirmation endpoint.
    """
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        
        if serializer.is_valid():
            try:
                uid = force_str(urlsafe_base64_decode(serializer.validated_data['uid']))
                user = User.objects.get(pk=uid)
                token = serializer.validated_data['token']
                
                if default_token_generator.check_token(user, token):
                    user.set_password(serializer.validated_data['new_password'])
                    user.save()
                    
                    return Response({
                        'message': 'Password reset successful'
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({
                        'error': 'Invalid token'
                    }, status=status.HTTP_400_BAD_REQUEST)
            
            except (TypeError, ValueError, OverflowError, User.DoesNotExist):
                return Response({
                    'error': 'Invalid token'
                }, status=status.HTTP_400_BAD_REQUEST)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(generics.ListCreateAPIView):
    """
    List and create user addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


class AddressDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Retrieve, update, and delete user addresses.
    """
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Address.objects.filter(user=self.request.user)


@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def user_dashboard(request):
    """
    User dashboard with summary information.
    """
    user = request.user
    
    # Get user statistics
    from apps.orders.models import Order
    from apps.reviews.models import Review
    
    total_orders = Order.objects.filter(user=user).count()
    total_reviews = Review.objects.filter(user=user).count()
    
    return Response({
        'user': UserSerializer(user).data,
        'statistics': {
            'total_orders': total_orders,
            'total_reviews': total_reviews,
            'addresses_count': user.addresses.count(),
        }
    })


# Password Reset Views using Email Service
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def request_password_reset(request):
    """
    Request password reset email
    """
    try:
        email = request.data.get('email')
        if not email:
            return Response(
                {'error': 'Email address is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Send password reset email
        result = PasswordResetService.send_password_reset_email(email)
        
        if result['success']:
            return Response(
                {'message': result['message']},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': result['message']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in password reset request: {str(e)}")
        return Response(
            {'error': 'An error occurred while processing your request.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_reset_code(request):
    """
    Verify password reset code
    """
    try:
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {'error': 'Email and code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify code
        result = PasswordResetService.verify_reset_code(email, code)
        
        if result['success']:
            return Response(
                {'message': 'Code is valid.'},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in code verification: {str(e)}")
        return Response(
            {'error': 'An error occurred while verifying the code.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def reset_password_confirm(request):
    """
    Reset password with code
    """
    try:
        email = request.data.get('email')
        code = request.data.get('code')
        new_password = request.data.get('new_password')
        confirm_password = request.data.get('confirm_password')
        
        if not all([email, code, new_password, confirm_password]):
            return Response(
                {'error': 'All fields are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if new_password != confirm_password:
            return Response(
                {'error': 'Passwords do not match.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(new_password) < 8:
            return Response(
                {'error': 'Password must be at least 8 characters long.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Reset password
        result = PasswordResetService.reset_password(email, code, new_password)
        
        if result['success']:
            return Response(
                {'message': result['message']},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': result.get('error', 'Password reset failed.')},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in password reset: {str(e)}")
        return Response(
            {'error': 'An error occurred while resetting your password.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Email Verification Views
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """
    Verify email with code
    """
    try:
        email = request.data.get('email')
        code = request.data.get('code')
        
        if not email or not code:
            return Response(
                {'error': 'Email and code are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if len(code) != 6:
            return Response(
                {'error': 'Please enter a valid 6-digit code.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify email code
        result = EmailVerificationService.verify_email_code(email, code)
        
        if result['success']:
            # Generate JWT tokens for the verified user
            user = result['user']
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token
            
            return Response({
                'message': result['message'],
                'user': UserSerializer(user).data,
                'tokens': {
                    'refresh': str(refresh),
                    'access': str(access_token),
                }
            }, status=status.HTTP_200_OK)
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in email verification: {str(e)}")
        return Response(
            {'error': 'An error occurred while verifying your email.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def resend_verification_code(request):
    """
    Resend email verification code
    """
    try:
        email = request.data.get('email')
        
        if not email:
            return Response(
                {'error': 'Email address is required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Resend verification code
        result = EmailVerificationService.resend_verification_code(email)
        
        if result['success']:
            return Response(
                {'message': result['message']},
                status=status.HTTP_200_OK
            )
        else:
            return Response(
                {'error': result['error']},
                status=status.HTTP_400_BAD_REQUEST
            )
            
    except Exception as e:
        logger.error(f"Error in resending verification code: {str(e)}")
        return Response(
            {'error': 'An error occurred while resending verification code.'},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# Two-Factor Authentication Views
class TwoFactorSetupView(APIView):
    """
    Setup Two-Factor Authentication
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            
            # Generate secret key
            secret = pyotp.random_base32()
            
            # Create TOTP instance
            totp = pyotp.TOTP(secret)
            
            # Generate QR code
            provisioning_uri = totp.provisioning_uri(
                name=user.email,
                issuer_name="Unique & Antique"
            )
            
            # Generate QR code image
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(provisioning_uri)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            # Convert to base64
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            # Generate backup codes
            backup_codes = [pyotp.random_base32()[:8] for _ in range(10)]
            
            # Store secret temporarily (will be saved when verified)
            request.session['temp_2fa_secret'] = secret
            request.session['temp_backup_codes'] = backup_codes
            
            # Debug session information
            logger.info(f"2FA Setup - Session key: {request.session.session_key}")
            logger.info(f"2FA Setup - Generated secret: {secret}")
            logger.info(f"2FA Setup - Provisioning URI: {provisioning_uri}")
            logger.info(f"2FA Setup - Current TOTP code: {totp.now()}")
            logger.info(f"2FA Setup - Session items: {list(request.session.keys())}")
            
            return Response({
                'secret': secret,
                'qr_code': f"data:image/png;base64,{qr_code_base64}",
                'backup_codes': backup_codes,
                'manual_entry_key': secret
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in 2FA setup: {str(e)}")
            return Response(
                {'error': 'An error occurred while setting up 2FA.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorVerifyView(APIView):
    """
    Verify and enable Two-Factor Authentication
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            code = request.data.get('code')
            
            # Debug the raw request data
            logger.info(f"2FA Verification - Raw request data: {request.data}")
            logger.info(f"2FA Verification - Extracted code: '{code}' (type: {type(code)})")
            
            if not code:
                return Response(
                    {'error': 'Verification code is required.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Get temporary secret from session
            secret = request.session.get('temp_2fa_secret')
            backup_codes = request.session.get('temp_backup_codes', [])
            
            # Debug session information
            logger.info(f"2FA Verification - Session key: {request.session.session_key}")
            logger.info(f"2FA Verification - Retrieved secret: {secret}")
            logger.info(f"2FA Verification - Has secret: {bool(secret)}")
            logger.info(f"2FA Verification - Session items: {list(request.session.keys())}")
            
            if not secret:
                return Response(
                    {'error': 'No setup session found. Please start 2FA setup again.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify the code with time window tolerance
            totp = pyotp.TOTP(secret)
            
            # Debug information
            import time
            import datetime
            current_time = int(time.time())
            expected_code = totp.now()
            readable_time = datetime.datetime.fromtimestamp(current_time).strftime('%Y-%m-%d %H:%M:%S')
            
            logger.info(f"2FA Verification - Input code: {code}")
            logger.info(f"2FA Verification - Expected code: {expected_code}")
            logger.info(f"2FA Verification - Current timestamp: {current_time}")
            logger.info(f"2FA Verification - Readable time: {readable_time}")
            
            # Check codes for different time windows to debug time sync
            logger.info("2FA Verification - Checking time windows...")
            for i in range(-10, 11):  # Check 10 windows before and after (10 minutes)
                test_time = current_time + (i * 30)  # 30 seconds per window
                test_totp = pyotp.TOTP(secret)
                test_code = test_totp.at(test_time)
                logger.info(f"2FA Verification - Window {i}: {test_code} (offset: {i*30}s)")
                if test_code == code:
                    logger.info(f"2FA Verification - ✅ CODE MATCH! Window {i} (offset: {i*30}s)")
                    # If we find a match, let's accept it manually
                    user.two_factor_enabled = True
                    user.two_factor_secret = secret
                    user.backup_codes = backup_codes
                    user.save()
                    
                    # Clear session data
                    request.session.pop('temp_2fa_secret', None)
                    request.session.pop('temp_backup_codes', None)
                    
                    return Response({
                        'message': '2FA has been successfully enabled.',
                        'backup_codes': backup_codes
                    }, status=status.HTTP_200_OK)
            
            # Try with a much larger window (5 minutes = 10 windows)
            # This should handle most time sync issues
            if totp.verify(code, valid_window=10):
                # Save 2FA settings to user
                user.two_factor_enabled = True
                user.two_factor_secret = secret
                user.backup_codes = backup_codes
                user.save()
                
                # Clear session data
                request.session.pop('temp_2fa_secret', None)
                request.session.pop('temp_backup_codes', None)
                
                return Response({
                    'message': '2FA has been successfully enabled.',
                    'backup_codes': backup_codes
                }, status=status.HTTP_200_OK)
            else:
                logger.warning(f"2FA Verification failed - Code mismatch for user {user.id}")
                return Response(
                    {'error': 'Invalid verification code. Please try with a fresh code from your authenticator app.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
        except Exception as e:
            logger.error(f"Error in 2FA verification: {str(e)}")
            return Response(
                {'error': 'An error occurred while verifying 2FA.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorDisableView(APIView):
    """
    Disable Two-Factor Authentication
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            password = request.data.get('password')
            
            if not password:
                return Response(
                    {'error': 'Password is required to disable 2FA.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify password
            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Disable 2FA
            user.two_factor_enabled = False
            user.two_factor_secret = None
            user.backup_codes = []
            user.save()
            
            return Response({
                'message': '2FA has been successfully disabled.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in 2FA disable: {str(e)}")
            return Response(
                {'error': 'An error occurred while disabling 2FA.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwoFactorStatusView(APIView):
    """
    Get Two-Factor Authentication status
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        user = request.user
        return Response({
            'two_factor_enabled': user.two_factor_enabled,
            'has_backup_codes': len(user.backup_codes) > 0 if user.backup_codes else False
        }, status=status.HTTP_200_OK)


# Account Deletion View
class DeleteAccountView(APIView):
    """
    Delete user account
    """
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        try:
            user = request.user
            password = request.data.get('password')
            confirmation = request.data.get('confirmation')
            
            if not password:
                return Response(
                    {'error': 'Password is required to delete account.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            if confirmation != 'DELETE':
                return Response(
                    {'error': 'Please type "DELETE" to confirm account deletion.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Verify password
            if not user.check_password(password):
                return Response(
                    {'error': 'Invalid password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Store user info for logging before deletion
            user_email = user.email
            user_id = user.id
            
            # Delete the user account (this will cascade delete related data)
            user.delete()
            
            logger.info(f"User account deleted: {user_email} (ID: {user_id})")
            
            return Response({
                'message': 'Your account has been successfully deleted.'
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Error in account deletion: {str(e)}")
            return Response(
                {'error': 'An error occurred while deleting your account.'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
