"""
Contact serializers for the Unique and Antique E-commerce Platform.
"""

from rest_framework import serializers
from .models import ContactMessage


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for contact message creation.
    """
    
    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'name',
            'email', 
            'subject',
            'message',
            'status',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'status', 'created_at', 'updated_at']
    
    def validate_message(self, value):
        """
        Validate message length.
        """
        if len(value.strip()) < 10:
            raise serializers.ValidationError(
                "Message must be at least 10 characters long."
            )
        return value.strip()
    
    def validate_name(self, value):
        """
        Validate name.
        """
        if len(value.strip()) < 2:
            raise serializers.ValidationError(
                "Name must be at least 2 characters long."
            )
        return value.strip()


class ContactMessageDetailSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for admin use.
    """
    
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id',
            'name',
            'email',
            'subject',
            'subject_display',
            'message',
            'status',
            'status_display',
            'admin_notes',
            'created_at',
            'updated_at',
            'responded_at'
        ]
