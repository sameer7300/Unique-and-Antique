"""
Custom admin forms for user-friendly product management
"""

from django import forms
from django.contrib import admin
from .models import Product
from .widgets import CareInstructionsWidget, AttributesWidget, UserFriendlyJSONField


class ProductAdminForm(forms.ModelForm):
    """
    Custom form for Product admin with user-friendly JSON fields
    """
    
    # Override JSON fields with user-friendly text areas
    care_instructions_text = UserFriendlyJSONField(
        json_type='list',
        required=False,
        label='Care Instructions (Simple Text)',
        help_text='Enter care instructions, one per line. Example:\n• Dust with soft cloth\n• Avoid direct sunlight\n• Keep away from moisture'
    )
    
    attributes_text = UserFriendlyJSONField(
        json_type='dict',
        required=False,
        label='Product Features & Specifications (Simple Text)',
        help_text='Enter features in "Feature: Value" format, one per line. Example:\n• Material: Solid Oak Wood\n• Color: Rich Brown\n• Weight: 15 kg'
    )
    
    class Meta:
        model = Product
        fields = '__all__'
        widgets = {
            'description': forms.Textarea(attrs={
                'rows': 6,
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Write a detailed description of your product. Describe its features, history, condition, and what makes it special...'
            }),
            'short_description': forms.Textarea(attrs={
                'rows': 3,
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Write a brief summary that will appear in product listings...'
            }),
            'condition': forms.TextInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'e.g., Authentic Antique, Vintage, Excellent Condition, Restored'
            }),
            'era': forms.TextInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'e.g., Victorian Era (1837-1901), Art Deco (1920s-1930s), Georgian Period'
            }),
            'material': forms.TextInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'e.g., Solid Oak Wood, Brass and Crystal, Sterling Silver, Mahogany'
            }),
            'tags': forms.TextInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Enter tags separated by commas: antique, furniture, victorian, wooden, table'
            }),
            'dimensions_length': forms.NumberInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Length in centimeters (e.g., 120)'
            }),
            'dimensions_width': forms.NumberInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Width in centimeters (e.g., 80)'
            }),
            'dimensions_height': forms.NumberInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Height in centimeters (e.g., 75)'
            }),
            'weight': forms.NumberInput(attrs={
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Weight in kilograms (e.g., 15.5)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Hide the original JSON fields
        if 'care_instructions' in self.fields:
            self.fields['care_instructions'].widget = forms.HiddenInput()
        if 'attributes' in self.fields:
            self.fields['attributes'].widget = forms.HiddenInput()
        
        # Pre-populate text fields with existing JSON data
        if self.instance and self.instance.pk:
            # Convert care_instructions JSON to text
            if self.instance.care_instructions:
                care_text = '\n'.join(self.instance.care_instructions)
                self.fields['care_instructions_text'].initial = care_text
            
            # Convert attributes JSON to text
            if self.instance.attributes:
                attr_text = '\n'.join(f"{k}: {v}" for k, v in self.instance.attributes.items())
                self.fields['attributes_text'].initial = attr_text
    
    def clean(self):
        """Convert text fields back to JSON before saving"""
        cleaned_data = super().clean()
        
        # Convert care instructions text to JSON
        care_text = cleaned_data.get('care_instructions_text', '')
        if care_text:
            care_lines = [line.strip() for line in care_text.split('\n') if line.strip()]
            cleaned_data['care_instructions'] = care_lines
        else:
            cleaned_data['care_instructions'] = []
        
        # Convert attributes text to JSON
        attr_text = cleaned_data.get('attributes_text', '')
        if attr_text:
            attributes = {}
            for line in attr_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    attributes[key.strip()] = value.strip()
                elif line:
                    # If no colon, use the line as both key and value
                    attributes[line] = line
            cleaned_data['attributes'] = attributes
        else:
            cleaned_data['attributes'] = {}
        
        return cleaned_data
    
    def save(self, commit=True):
        """Ensure JSON fields are properly set before saving"""
        instance = super().save(commit=False)
        
        # Set the JSON fields from our text fields
        care_text = self.cleaned_data.get('care_instructions_text', '')
        if care_text:
            care_lines = [line.strip() for line in care_text.split('\n') if line.strip()]
            instance.care_instructions = care_lines
        
        attr_text = self.cleaned_data.get('attributes_text', '')
        if attr_text:
            attributes = {}
            for line in attr_text.split('\n'):
                line = line.strip()
                if line and ':' in line:
                    key, value = line.split(':', 1)
                    attributes[key.strip()] = value.strip()
                elif line:
                    attributes[line] = line
            instance.attributes = attributes
        
        if commit:
            instance.save()
        return instance


class ProductImageAdminForm(forms.ModelForm):
    """Enhanced form for product images"""
    
    class Meta:
        model = Product
        fields = '__all__'
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Add helpful styling to alt_text field
        if 'alt_text' in self.fields:
            self.fields['alt_text'].widget.attrs.update({
                'style': 'width: 100%; border-radius: 8px; padding: 12px;',
                'placeholder': 'Describe the image for accessibility (e.g., "Victorian oak dining table with carved legs")'
            })
