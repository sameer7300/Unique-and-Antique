"""
Admin views for the accounts app.
"""

from django.contrib.auth import get_user_model
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from django.core.paginator import Paginator

from .models import User, Address
from .serializers import UserSerializer

User = get_user_model()


class AdminUserStatsView(APIView):
    """Get user statistics for admin dashboard."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get date ranges
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Calculate stats
        total_users = User.objects.count()
        active_users = User.objects.filter(is_active=True).count()
        verified_users = User.objects.filter(is_verified=True).count()
        admin_users = User.objects.filter(Q(is_staff=True) | Q(is_superuser=True)).count()
        new_users = User.objects.filter(date_joined__gte=last_30_days).count()
        
        return Response({
            'total': total_users,
            'active': active_users,
            'verified': verified_users,
            'admins': admin_users,
            'new': new_users,
        })


class AdminUserListView(ListAPIView):
    """List all users for admin with pagination and filtering."""
    permission_classes = [IsAdminUser]
    serializer_class = UserSerializer
    
    def get_queryset(self):
        queryset = User.objects.all().select_related('profile').prefetch_related('addresses')
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(email__icontains=search) |
                Q(username__icontains=search)
            )
        
        # Role filtering
        role = self.request.query_params.get('role', None)
        if role == 'admin':
            queryset = queryset.filter(Q(is_staff=True) | Q(is_superuser=True))
        elif role == 'customer':
            queryset = queryset.filter(is_staff=False, is_superuser=False)
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter == 'active':
            queryset = queryset.filter(is_active=True)
        elif status_filter == 'inactive':
            queryset = queryset.filter(is_active=False)
        
        return queryset.order_by('-date_joined')


@api_view(['GET'])
@permission_classes([IsAdminUser])
def admin_activity_recent(request):
    """Get recent activity for admin dashboard."""
    
    # Get recent user registrations
    recent_users = User.objects.filter(
        date_joined__gte=timezone.now() - timedelta(days=7)
    ).order_by('-date_joined')[:5]
    
    activities = []
    
    # Add user registration activities
    for user in recent_users:
        activities.append({
            'id': f'user_reg_{user.id}',
            'type': 'user_registration',
            'title': f'New user registered: {user.get_full_name() or user.username}',
            'description': f'{user.email} joined the platform',
            'timestamp': user.date_joined.isoformat(),
            'user': {
                'id': user.id,
                'name': user.get_full_name() or user.username,
                'email': user.email,
                'is_active': user.is_active,
                'is_verified': user.is_verified,
                'status': 'verified' if user.is_verified else ('active' if user.is_active else 'inactive')
            }
        })
    
    # Sort activities by timestamp (most recent first)
    activities.sort(key=lambda x: x['timestamp'], reverse=True)
    
    return Response({
        'results': activities[:10],  # Return last 10 activities
        'count': len(activities)
    })


class AdminUserDetailView(APIView):
    """Get, update, or delete a specific user."""
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            user = User.objects.select_related('profile').prefetch_related('addresses').get(pk=pk)
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            
            # Update allowed fields
            allowed_fields = ['is_active', 'is_staff', 'first_name', 'last_name']
            for field in allowed_fields:
                if field in request.data:
                    setattr(user, field, request.data[field])
            
            user.save()
            serializer = UserSerializer(user)
            return Response(serializer.data)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            user = User.objects.get(pk=pk)
            if user.is_superuser:
                return Response({'error': 'Cannot delete superuser'}, status=status.HTTP_400_BAD_REQUEST)
            user.delete()
            return Response({'message': 'User deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_404_NOT_FOUND)
