"""
Custom Cloudinary storage configuration for Unique & Antique
"""
from cloudinary_storage.storage import MediaCloudinaryStorage
from django.conf import settings
import cloudinary.uploader
import cloudinary.api


class CustomCloudinaryStorage(MediaCloudinaryStorage):
    """
    Custom Cloudinary storage with enhanced functionality
    """
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set folder structure for organized storage
        self.folder = getattr(settings, 'CLOUDINARY_FOLDER', 'unique-antique')
    
    def _save(self, name, content):
        """
        Override save method to organize files in folders
        """
        # Determine folder based on file type
        if name.startswith('products/'):
            folder = f"{self.folder}/products"
        elif name.startswith('users/'):
            folder = f"{self.folder}/users"
        elif name.startswith('reviews/'):
            folder = f"{self.folder}/reviews"
        else:
            folder = f"{self.folder}/misc"
        
        # Upload with folder structure
        options = {
            'folder': folder,
            'resource_type': 'auto',
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
        }
        
        # Upload to Cloudinary
        result = cloudinary.uploader.upload(content, **options)
        return result['public_id']
    
    def url(self, name):
        """
        Return the URL for accessing the file
        """
        if not name:
            return None
        
        # Generate secure URL
        return cloudinary.utils.cloudinary_url(
            name,
            secure=True,
            quality='auto',
            fetch_format='auto'
        )[0]


class ProductImageStorage(CustomCloudinaryStorage):
    """
    Specialized storage for product images with optimizations
    """
    
    def _save(self, name, content):
        """
        Save product images with specific optimizations
        """
        folder = f"{self.folder}/products"
        
        options = {
            'folder': folder,
            'resource_type': 'image',
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
            'transformation': [
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'},
                {'width': 1200, 'height': 1200, 'crop': 'limit'},
            ]
        }
        
        result = cloudinary.uploader.upload(content, **options)
        return result['public_id']


class UserAvatarStorage(CustomCloudinaryStorage):
    """
    Specialized storage for user avatars
    """
    
    def _save(self, name, content):
        """
        Save user avatars with specific optimizations
        """
        folder = f"{self.folder}/users/avatars"
        
        options = {
            'folder': folder,
            'resource_type': 'image',
            'use_filename': True,
            'unique_filename': True,
            'overwrite': True,  # Allow overwrite for avatars
            'transformation': [
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'},
                {'width': 300, 'height': 300, 'crop': 'fill', 'gravity': 'face'},
                {'radius': 'max'},  # Make circular
            ]
        }
        
        result = cloudinary.uploader.upload(content, **options)
        return result['public_id']


class ReviewImageStorage(CustomCloudinaryStorage):
    """
    Specialized storage for review images
    """
    
    def _save(self, name, content):
        """
        Save review images with specific optimizations
        """
        folder = f"{self.folder}/reviews"
        
        options = {
            'folder': folder,
            'resource_type': 'image',
            'use_filename': True,
            'unique_filename': True,
            'overwrite': False,
            'transformation': [
                {'quality': 'auto:good'},
                {'fetch_format': 'auto'},
                {'width': 800, 'height': 600, 'crop': 'limit'},
            ]
        }
        
        result = cloudinary.uploader.upload(content, **options)
        return result['public_id']
