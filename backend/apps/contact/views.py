"""
Contact views for the Unique and Antique E-commerce Platform.
"""

from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import logging

from .models import ContactMessage
from .serializers import ContactMessageSerializer, ContactMessageDetailSerializer
from .services import ContactEmailService

logger = logging.getLogger(__name__)


class ContactMessageCreateView(generics.CreateAPIView):
    """
    Create a new contact message.
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """
        Create contact message and send emails.
        """
        try:
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                logger.warning(f"Contact form validation failed: {serializer.errors}")
                return Response(
                    {
                        'error': 'Please check your form data and try again.',
                        'validation_errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Save the contact message
            contact_message = serializer.save()
            logger.info(f"Contact message created with ID: {contact_message.id}")
            
            # Send emails (don't fail the request if email sending fails)
            email_sent = False
            try:
                email_sent = ContactEmailService.send_contact_emails(contact_message)
                if email_sent:
                    logger.info(f"Emails sent successfully for contact message {contact_message.id}")
                else:
                    logger.warning(f"Failed to send emails for contact message {contact_message.id}")
            except Exception as e:
                logger.error(f"Exception while sending emails for contact message {contact_message.id}: {str(e)}")
            
            return Response(
                {
                    'message': 'Your message has been sent successfully. We will get back to you within 24 hours.',
                    'data': serializer.data,
                    'email_sent': email_sent
                },
                status=status.HTTP_201_CREATED
            )
            
        except Exception as e:
            logger.error(f"Error creating contact message: {str(e)}")
            return Response(
                {
                    'error': 'Failed to submit contact message. Please try again.',
                    'details': str(e) if settings.DEBUG else None
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ContactMessageListView(generics.ListAPIView):
    """
    List all contact messages (admin only).
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageDetailSerializer
    permission_classes = [permissions.IsAdminUser]
    
    def get_queryset(self):
        """
        Filter by status if provided.
        """
        queryset = super().get_queryset()
        status_filter = self.request.query_params.get('status', None)
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        return queryset


class ContactMessageDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update contact message (admin only).
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageDetailSerializer
    permission_classes = [permissions.IsAdminUser]


@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def contact_subjects(request):
    """
    Get available contact subjects.
    """
    subjects = [
        {'value': choice[0], 'label': choice[1]}
        for choice in ContactMessage.SUBJECT_CHOICES
    ]
    return Response({'subjects': subjects})
