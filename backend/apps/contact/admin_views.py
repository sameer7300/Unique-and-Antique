"""
Admin views for the contact app.
"""

from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.generics import ListAPIView

from .models import ContactMessage
from .serializers import ContactMessageSerializer


class AdminContactStatsView(APIView):
    """Get contact statistics for admin dashboard."""
    permission_classes = [IsAdminUser]
    
    def get(self, request):
        # Get date ranges
        now = timezone.now()
        last_30_days = now - timedelta(days=30)
        
        # Calculate stats
        total_messages = ContactMessage.objects.count()
        pending_messages = ContactMessage.objects.filter(status='pending').count()
        resolved_messages = ContactMessage.objects.filter(status='resolved').count()
        new_messages = ContactMessage.objects.filter(created_at__gte=last_30_days).count()
        
        return Response({
            'total': total_messages,
            'pending': pending_messages,
            'resolved': resolved_messages,
            'new': new_messages,
        })


class AdminContactListView(ListAPIView):
    """List all contact messages for admin with pagination and filtering."""
    permission_classes = [IsAdminUser]
    serializer_class = ContactMessageSerializer
    
    def get_queryset(self):
        queryset = ContactMessage.objects.all()
        
        # Search functionality
        search = self.request.query_params.get('search', None)
        if search:
            queryset = queryset.filter(
                Q(name__icontains=search) |
                Q(email__icontains=search) |
                Q(subject__icontains=search) |
                Q(message__icontains=search)
            )
        
        # Status filtering
        status_filter = self.request.query_params.get('status', None)
        if status_filter and status_filter != 'all':
            queryset = queryset.filter(status=status_filter)
        
        return queryset.order_by('-created_at')


class AdminContactDetailView(APIView):
    """Get, update, or delete a specific contact message."""
    permission_classes = [IsAdminUser]
    
    def get(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            serializer = ContactMessageSerializer(message)
            return Response(serializer.data)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def patch(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            
            # Update allowed fields
            allowed_fields = ['status', 'admin_notes']
            for field in allowed_fields:
                if field in request.data:
                    setattr(message, field, request.data[field])
            
            message.save()
            serializer = ContactMessageSerializer(message)
            return Response(serializer.data)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
    
    def delete(self, request, pk):
        try:
            message = ContactMessage.objects.get(pk=pk)
            message.delete()
            return Response({'message': 'Contact message deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except ContactMessage.DoesNotExist:
            return Response({'error': 'Contact message not found'}, status=status.HTTP_404_NOT_FOUND)
