from rest_framework import serializers
from .models import NewsletterSubscriber


class NewsletterSubscriberSerializer(serializers.ModelSerializer):
    """Serializer for newsletter subscription"""
    
    class Meta:
        model = NewsletterSubscriber
        fields = ['email', 'name']
        extra_kwargs = {
            'email': {
                'required': True,
                'error_messages': {
                    'required': 'Email address is required.',
                    'invalid': 'Please enter a valid email address.',
                    'unique': 'This email is already subscribed to our newsletter.'
                }
            },
            'name': {
                'required': False,
                'allow_blank': True
            }
        }
    
    def validate_email(self, value):
        """Custom email validation"""
        if not value:
            raise serializers.ValidationError("Email address is required.")
        
        # Check if email is already subscribed and active
        existing_subscriber = NewsletterSubscriber.objects.filter(
            email=value,
            is_active=True
        ).first()
        
        if existing_subscriber:
            raise serializers.ValidationError("This email is already subscribed to our newsletter.")
        
        return value.lower().strip()
    
    def create(self, validated_data):
        """Create or reactivate newsletter subscription"""
        email = validated_data['email']
        
        # Check if there's an inactive subscription
        existing_subscriber = NewsletterSubscriber.objects.filter(email=email).first()
        
        if existing_subscriber and not existing_subscriber.is_active:
            # Reactivate existing subscription
            existing_subscriber.resubscribe()
            existing_subscriber.name = validated_data.get('name', existing_subscriber.name)
            existing_subscriber.save()
            return existing_subscriber
        
        # Create new subscription
        return super().create(validated_data)


class NewsletterUnsubscribeSerializer(serializers.Serializer):
    """Serializer for newsletter unsubscription"""
    email = serializers.EmailField(
        required=True,
        error_messages={
            'required': 'Email address is required.',
            'invalid': 'Please enter a valid email address.'
        }
    )
    
    def validate_email(self, value):
        """Validate that email exists and is active"""
        try:
            subscriber = NewsletterSubscriber.objects.get(
                email=value.lower().strip(),
                is_active=True
            )
            self.instance = subscriber
            return value.lower().strip()
        except NewsletterSubscriber.DoesNotExist:
            raise serializers.ValidationError("This email is not subscribed to our newsletter.")
