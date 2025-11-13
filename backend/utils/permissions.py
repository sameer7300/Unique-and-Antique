"""
Custom permissions for the Unique and Antique E-commerce Platform.
"""

from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow owners of an object to edit it.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed for any request,
        # so we'll always allow GET, HEAD or OPTIONS requests.
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner of the object.
        return obj.user == request.user


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission to only allow admin users to edit objects.
    """
    
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        
        return request.user and request.user.is_authenticated and request.user.is_admin_user


class IsVerifiedPurchaser(permissions.BasePermission):
    """
    Permission to check if user has purchased the product (for reviews).
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        # For POST requests (creating reviews), check if user has purchased the product
        if request.method == 'POST':
            product_id = request.data.get('product')
            if product_id:
                from apps.orders.models import Order, OrderItem
                
                # Check if user has a delivered order with this product
                has_purchased = OrderItem.objects.filter(
                    order__user=request.user,
                    order__status='delivered',
                    product_id=product_id
                ).exists()
                
                return has_purchased
        
        return True


class IsCustomerOrAdmin(permissions.BasePermission):
    """
    Permission for customer-specific actions or admin access.
    """
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        return request.user.is_customer or request.user.is_admin_user


class IsAdminUser(permissions.BasePermission):
    """
    Permission for admin users only.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin_user
        )


class IsStaffOrAdmin(permissions.BasePermission):
    """
    Permission for staff or admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff_user or request.user.is_admin_user)
        )


class CanModerateReviews(permissions.BasePermission):
    """
    Permission for users who can moderate reviews.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff_user or request.user.is_admin_user)
        )


class CanManageOrders(permissions.BasePermission):
    """
    Permission for users who can manage orders.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            (request.user.is_staff_user or request.user.is_admin_user)
        )


class CanProcessPayments(permissions.BasePermission):
    """
    Permission for users who can process payments and refunds.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and 
            request.user.is_authenticated and 
            request.user.is_admin_user
        )
