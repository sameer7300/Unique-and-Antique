#!/usr/bin/env python
"""
Test script to verify Cloudinary configuration
"""
import os
import sys
import django
from pathlib import Path
from io import BytesIO
from PIL import Image

# Add the backend directory to Python path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
import cloudinary
import cloudinary.uploader
import cloudinary.api

def test_cloudinary_configuration():
    """Test Cloudinary configuration"""
    print("Testing Cloudinary configuration...")
    print(f"Cloud Name: {settings.CLOUDINARY_STORAGE['CLOUD_NAME']}")
    print(f"API Key: {settings.CLOUDINARY_STORAGE['API_KEY']}")
    print(f"Folder: {settings.CLOUDINARY_STORAGE['FOLDER']}")
    print(f"Secure: {settings.CLOUDINARY_STORAGE['SECURE']}")
    print(f"Default Storage: {settings.DEFAULT_FILE_STORAGE}")
    print("-" * 50)

def test_cloudinary_connection():
    """Test connection to Cloudinary"""
    try:
        print("Testing Cloudinary API connection...")
        result = cloudinary.api.ping()
        print(f"✅ Cloudinary connection successful: {result}")
        return True
    except Exception as e:
        print(f"❌ Cloudinary connection failed: {e}")
        return False

def create_test_image():
    """Create a test image for upload"""
    # Create a simple test image
    img = Image.new('RGB', (200, 200), color='red')
    img_io = BytesIO()
    img.save(img_io, format='JPEG')
    img_io.seek(0)
    return ContentFile(img_io.getvalue(), name='test_image.jpg')

def test_file_upload():
    """Test file upload to Cloudinary"""
    try:
        print("Testing file upload to Cloudinary...")
        
        # Create test image
        test_image = create_test_image()
        
        # Upload using Django's default storage
        file_name = default_storage.save('test/test_image.jpg', test_image)
        print(f"✅ File uploaded successfully: {file_name}")
        
        # Get the URL
        file_url = default_storage.url(file_name)
        print(f"✅ File URL: {file_url}")
        
        # Clean up - delete the test file
        try:
            default_storage.delete(file_name)
            print("✅ Test file cleaned up")
        except Exception as e:
            print(f"⚠️  Could not delete test file: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ File upload failed: {e}")
        return False

def test_cloudinary_direct_upload():
    """Test direct upload to Cloudinary"""
    try:
        print("Testing direct Cloudinary upload...")
        
        # Create test image
        test_image = create_test_image()
        
        # Upload directly to Cloudinary
        result = cloudinary.uploader.upload(
            test_image,
            folder="unique-antique/test",
            resource_type="image",
            use_filename=True,
            unique_filename=True
        )
        
        print(f"✅ Direct upload successful:")
        print(f"   Public ID: {result['public_id']}")
        print(f"   URL: {result['secure_url']}")
        print(f"   Format: {result['format']}")
        print(f"   Size: {result['bytes']} bytes")
        
        # Clean up - delete the test file
        try:
            cloudinary.uploader.destroy(result['public_id'])
            print("✅ Test file cleaned up from Cloudinary")
        except Exception as e:
            print(f"⚠️  Could not delete test file from Cloudinary: {e}")
        
        return True
        
    except Exception as e:
        print(f"❌ Direct Cloudinary upload failed: {e}")
        return False

def test_folder_structure():
    """Test folder structure creation"""
    try:
        print("Testing folder structure...")
        
        folders = ['products', 'users', 'reviews']
        results = []
        
        for folder in folders:
            test_image = create_test_image()
            result = cloudinary.uploader.upload(
                test_image,
                folder=f"unique-antique/{folder}",
                resource_type="image",
                public_id=f"test_{folder}_image"
            )
            results.append(result)
            print(f"✅ Uploaded to folder '{folder}': {result['public_id']}")
        
        # Clean up
        for result in results:
            try:
                cloudinary.uploader.destroy(result['public_id'])
            except:
                pass
        
        print("✅ Folder structure test completed")
        return True
        
    except Exception as e:
        print(f"❌ Folder structure test failed: {e}")
        return False

def main():
    """Main function"""
    print("=" * 60)
    print("CLOUDINARY CONFIGURATION TEST")
    print("=" * 60)
    
    test_cloudinary_configuration()
    
    tests = [
        ("Connection Test", test_cloudinary_connection),
        ("File Upload Test", test_file_upload),
        ("Direct Upload Test", test_cloudinary_direct_upload),
        ("Folder Structure Test", test_folder_structure),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n🧪 Running {test_name}...")
        try:
            if test_func():
                passed += 1
                print(f"✅ {test_name} PASSED")
            else:
                print(f"❌ {test_name} FAILED")
        except Exception as e:
            print(f"❌ {test_name} FAILED with exception: {e}")
    
    print("\n" + "=" * 60)
    print(f"TEST RESULTS: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 ALL CLOUDINARY TESTS PASSED!")
        print("Your Cloudinary configuration is working correctly.")
    else:
        print("❌ SOME TESTS FAILED!")
        print("Please check your Cloudinary settings and credentials.")
    print("=" * 60)

if __name__ == "__main__":
    main()
