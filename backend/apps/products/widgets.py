"""
Custom admin widgets for user-friendly JSON field management
"""

from django import forms
from django.utils.safestring import mark_safe
import json


class SimpleTextToJSONWidget(forms.Textarea):
    """
    Widget that allows admins to enter simple text and converts it to JSON
    """
    
    def __init__(self, json_type='list', *args, **kwargs):
        self.json_type = json_type  # 'list' or 'dict'
        super().__init__(*args, **kwargs)
        
    def format_value(self, value):
        """Convert JSON back to simple text for editing"""
        if not value:
            return ''
            
        try:
            if self.json_type == 'list' and isinstance(value, list):
                # Convert list to newline-separated text
                return '\n'.join(str(item) for item in value)
            elif self.json_type == 'dict' and isinstance(value, dict):
                # Convert dict to "key: value" format
                return '\n'.join(f"{key}: {val}" for key, val in value.items())
            else:
                return str(value)
        except (TypeError, ValueError):
            return str(value)
    
    def value_from_datadict(self, data, files, name):
        """Convert simple text input to JSON"""
        text_value = data.get(name, '')
        
        if not text_value.strip():
            return [] if self.json_type == 'list' else {}
            
        try:
            lines = [line.strip() for line in text_value.split('\n') if line.strip()]
            
            if self.json_type == 'list':
                # Return as list
                return lines
            elif self.json_type == 'dict':
                # Parse "key: value" format
                result = {}
                for line in lines:
                    if ':' in line:
                        key, value = line.split(':', 1)
                        result[key.strip()] = value.strip()
                    else:
                        # If no colon, use line as both key and value
                        result[line] = line
                return result
        except Exception:
            # If parsing fails, return the text as-is
            return text_value
            
        return text_value


class CareInstructionsWidget(SimpleTextToJSONWidget):
    """Specific widget for care instructions (list format)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(json_type='list', *args, **kwargs)
        self.attrs.update({
            'rows': 6,
            'cols': 80,
            'placeholder': 'Enter care instructions, one per line:\n\nDust with soft cloth\nAvoid direct sunlight\nKeep away from moisture\nUse wood polish monthly',
            'style': 'width: 100%; font-family: monospace; background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 12px;'
        })


class AttributesWidget(SimpleTextToJSONWidget):
    """Specific widget for product attributes (dict format)"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(json_type='dict', *args, **kwargs)
        self.attrs.update({
            'rows': 8,
            'cols': 80,
            'placeholder': 'Enter product features, one per line in "Feature: Value" format:\n\nMaterial: Solid Oak Wood\nColor: Rich Brown\nWeight: 15 kg\nDimensions: 120cm x 80cm x 45cm\nStyle: Victorian\nCondition: Excellent',
            'style': 'width: 100%; font-family: monospace; background: #f8f9fa; border: 2px solid #e9ecef; border-radius: 8px; padding: 12px;'
        })


class UserFriendlyJSONField(forms.CharField):
    """
    Custom form field that uses our simple text widgets
    """
    
    def __init__(self, json_type='list', *args, **kwargs):
        self.json_type = json_type
        if json_type == 'list':
            kwargs['widget'] = CareInstructionsWidget()
        else:
            kwargs['widget'] = AttributesWidget()
        super().__init__(*args, **kwargs)
        
    def to_python(self, value):
        """Convert the widget value to proper JSON"""
        if not value:
            return [] if self.json_type == 'list' else {}
        return value
        
    def validate(self, value):
        """Validate the JSON structure"""
        super().validate(value)
        if self.json_type == 'list' and not isinstance(value, list):
            raise forms.ValidationError("Care instructions must be a list")
        elif self.json_type == 'dict' and not isinstance(value, dict):
            raise forms.ValidationError("Attributes must be key-value pairs")
