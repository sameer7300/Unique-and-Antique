"""
Custom exceptions for the Unique and Antique E-commerce Platform.
"""

from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status
from django.core.exceptions import ValidationError as DjangoValidationError


class InsufficientStockError(Exception):
    """
    Exception raised when there's insufficient stock for a product.
    """
    def __init__(self, product, requested_quantity, available_stock):
        self.product = product
        self.requested_quantity = requested_quantity
        self.available_stock = available_stock
        super().__init__(
            f"Insufficient stock for {product}. "
            f"Requested: {requested_quantity}, Available: {available_stock}"
        )


class PaymentProcessingError(Exception):
    """
    Exception raised when payment processing fails.
    """
    def __init__(self, message, error_code=None, provider_error=None):
        self.error_code = error_code
        self.provider_error = provider_error
        super().__init__(message)


class OrderProcessingError(Exception):
    """
    Exception raised when order processing fails.
    """
    pass


class CartError(Exception):
    """
    Exception raised for cart-related errors.
    """
    pass


class ReviewError(Exception):
    """
    Exception raised for review-related errors.
    """
    pass


def custom_exception_handler(exc, context):
    """
    Custom exception handler that provides consistent error responses.
    """
    # Call REST framework's default exception handler first
    response = exception_handler(exc, context)
    
    # If the response is None, it means the exception wasn't handled by DRF
    if response is None:
        # Handle custom exceptions
        if isinstance(exc, InsufficientStockError):
            return Response({
                'error': 'insufficient_stock',
                'message': str(exc),
                'details': {
                    'product': exc.product.title if hasattr(exc.product, 'title') else str(exc.product),
                    'requested_quantity': exc.requested_quantity,
                    'available_stock': exc.available_stock
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, PaymentProcessingError):
            return Response({
                'error': 'payment_processing_error',
                'message': str(exc),
                'details': {
                    'error_code': exc.error_code,
                    'provider_error': exc.provider_error
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, OrderProcessingError):
            return Response({
                'error': 'order_processing_error',
                'message': str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, CartError):
            return Response({
                'error': 'cart_error',
                'message': str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, ReviewError):
            return Response({
                'error': 'review_error',
                'message': str(exc)
            }, status=status.HTTP_400_BAD_REQUEST)
        
        elif isinstance(exc, DjangoValidationError):
            return Response({
                'error': 'validation_error',
                'message': 'Validation failed',
                'details': exc.message_dict if hasattr(exc, 'message_dict') else [str(exc)]
            }, status=status.HTTP_400_BAD_REQUEST)
    
    # Customize the response format for DRF exceptions
    if response is not None:
        custom_response_data = {
            'error': 'api_error',
            'message': 'An error occurred',
            'details': response.data
        }
        
        # Add specific error types for common DRF exceptions
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            custom_response_data['error'] = 'validation_error'
            custom_response_data['message'] = 'Validation failed'
        elif response.status_code == status.HTTP_401_UNAUTHORIZED:
            custom_response_data['error'] = 'authentication_error'
            custom_response_data['message'] = 'Authentication required'
        elif response.status_code == status.HTTP_403_FORBIDDEN:
            custom_response_data['error'] = 'permission_error'
            custom_response_data['message'] = 'Permission denied'
        elif response.status_code == status.HTTP_404_NOT_FOUND:
            custom_response_data['error'] = 'not_found'
            custom_response_data['message'] = 'Resource not found'
        elif response.status_code == status.HTTP_405_METHOD_NOT_ALLOWED:
            custom_response_data['error'] = 'method_not_allowed'
            custom_response_data['message'] = 'Method not allowed'
        elif response.status_code >= 500:
            custom_response_data['error'] = 'server_error'
            custom_response_data['message'] = 'Internal server error'
        
        response.data = custom_response_data
    
    return response
