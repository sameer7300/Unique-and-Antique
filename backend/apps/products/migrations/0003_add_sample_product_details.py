# Generated manually

from django.db import migrations


def add_sample_product_details(apps, schema_editor):
    """Add sample product details to existing products."""
    Product = apps.get_model('products', 'Product')
    
    # Sample data for different product types
    sample_data = [
        {
            'condition': 'Authentic Antique',
            'era': 'Victorian Era (1837-1901)',
            'material': 'Solid Oak Wood',
            'care_instructions': [
                'Dust regularly with a soft, dry cloth',
                'Avoid direct sunlight to prevent fading',
                'Use furniture polish sparingly',
                'Keep away from heat sources',
                'Handle with care to preserve original finish'
            ]
        },
        {
            'condition': 'Vintage Collectible',
            'era': 'Art Deco Period (1920s-1930s)',
            'material': 'Brass and Crystal',
            'care_instructions': [
                'Clean with mild soap and water',
                'Dry immediately to prevent water spots',
                'Polish brass components monthly',
                'Store in protective wrapping when not displayed'
            ]
        },
        {
            'condition': 'Restored Antique',
            'era': 'Georgian Period (1714-1830)',
            'material': 'Mahogany with Brass Fittings',
            'care_instructions': [
                'Use only museum-quality cleaning products',
                'Maintain stable temperature and humidity',
                'Inspect regularly for signs of wear',
                'Professional restoration recommended for repairs'
            ]
        }
    ]
    
    products = Product.objects.all()[:10]  # Update first 10 products
    
    for i, product in enumerate(products):
        data_index = i % len(sample_data)
        sample = sample_data[data_index]
        
        product.condition = sample['condition']
        product.era = sample['era']
        product.material = sample['material']
        product.care_instructions = sample['care_instructions']
        product.authenticity_verified = True
        
        # Add some sample dimensions if not already set
        if not product.dimensions_length:
            product.dimensions_length = 45.5 + (i * 2.5)
            product.dimensions_width = 30.0 + (i * 1.5)
            product.dimensions_height = 25.0 + (i * 1.0)
        
        if not product.weight:
            product.weight = 2.5 + (i * 0.5)
        
        product.save()


def reverse_sample_product_details(apps, schema_editor):
    """Remove sample product details."""
    Product = apps.get_model('products', 'Product')
    
    Product.objects.all().update(
        condition='',
        era='',
        material='',
        care_instructions=[],
        authenticity_verified=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ('products', '0002_product_authenticity_verified_and_more'),
    ]

    operations = [
        migrations.RunPython(
            add_sample_product_details,
            reverse_sample_product_details
        ),
    ]
