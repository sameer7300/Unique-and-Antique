"""
Serializers for the products app.
"""

from rest_framework import serializers
from django.db.models import Avg
from .models import Category, Brand, Product, ProductImage, ProductVariant


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for Category model.
    """
    children = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    full_name = serializers.ReadOnlyField()
    
    class Meta:
        model = Category
        fields = [
            'id', 'name', 'slug', 'description', 'parent', 'image',
            'is_active', 'sort_order', 'children', 'product_count',
            'full_name', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_children(self, obj):
        """Get child categories."""
        if obj.children.exists():
            return CategorySerializer(
                obj.children.filter(is_active=True),
                many=True,
                context=self.context
            ).data
        return []
    
    def get_product_count(self, obj):
        """Get number of active products in this category."""
        return obj.products.filter(status='active').count()


class BrandSerializer(serializers.ModelSerializer):
    """
    Serializer for Brand model.
    """
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Brand
        fields = [
            'id', 'name', 'slug', 'description', 'logo', 'website',
            'is_active', 'product_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']
    
    def get_product_count(self, obj):
        """Get number of active products for this brand."""
        return obj.products.filter(status='active').count()


class ProductImageSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductImage model.
    """
    
    class Meta:
        model = ProductImage
        fields = [
            'id', 'image', 'alt_text', 'position', 'is_primary', 'created_at'
        ]
        read_only_fields = ['created_at']


class ProductVariantSerializer(serializers.ModelSerializer):
    """
    Serializer for ProductVariant model.
    """
    is_in_stock = serializers.ReadOnlyField()
    
    class Meta:
        model = ProductVariant
        fields = [
            'id', 'name', 'sku', 'price', 'stock', 'attributes',
            'is_active', 'is_in_stock', 'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']


class ProductListSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model in list views (minimal data).
    """
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'short_description', 'category', 'brand',
            'price', 'compare_price', 'sku', 'stock', 'primary_image',
            'average_rating', 'review_count', 'is_in_stock', 'is_low_stock',
            'discount_percentage', 'is_featured', 'created_at'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image:
            return ProductImageSerializer(primary_image, context=self.context).data
        return None


class ProductDetailSerializer(serializers.ModelSerializer):
    """
    Serializer for Product model in detail views (complete data).
    """
    category = CategorySerializer(read_only=True)
    brand = BrandSerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    is_in_stock = serializers.ReadOnlyField()
    is_low_stock = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    related_products = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'category', 'brand', 'price', 'compare_price', 'cost_price',
            'sku', 'stock', 'low_stock_threshold', 'track_inventory',
            'allow_backorders', 'weight', 'dimensions_length',
            'dimensions_width', 'dimensions_height', 'meta_title',
            'meta_description', 'tags', 'status', 'is_featured',
            'is_digital', 'requires_shipping', 'attributes', 'care_instructions',
            'condition', 'era', 'material', 'authenticity_verified', 'images',
            'variants', 'average_rating', 'review_count', 'is_in_stock',
            'is_low_stock', 'discount_percentage', 'related_products',
            'created_at', 'updated_at', 'published_at'
        ]
        read_only_fields = ['created_at', 'updated_at', 'published_at']
    
    def get_related_products(self, obj):
        """Get related products from same category."""
        related = Product.objects.filter(
            category=obj.category,
            status='active'
        ).exclude(id=obj.id)[:4]
        
        return ProductListSerializer(
            related,
            many=True,
            context=self.context
        ).data


class ProductCreateUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for creating and updating products.
    """
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = Product
        fields = [
            'title', 'description', 'short_description', 'category', 'brand',
            'price', 'compare_price', 'cost_price', 'sku', 'stock',
            'low_stock_threshold', 'track_inventory', 'allow_backorders',
            'weight', 'dimensions_length', 'dimensions_width',
            'dimensions_height', 'meta_title', 'meta_description', 'tags',
            'status', 'is_featured', 'is_digital', 'requires_shipping',
            'attributes', 'care_instructions', 'condition', 'era', 'material',
            'authenticity_verified', 'images', 'variants'
        ]
    
    def validate_sku(self, value):
        """Validate SKU uniqueness."""
        if self.instance:
            # Update case - exclude current instance
            if Product.objects.exclude(id=self.instance.id).filter(sku=value).exists():
                raise serializers.ValidationError("SKU must be unique.")
        else:
            # Create case
            if Product.objects.filter(sku=value).exists():
                raise serializers.ValidationError("SKU must be unique.")
        return value
    
    def validate_price(self, value):
        """Validate price is positive."""
        if value <= 0:
            raise serializers.ValidationError("Price must be positive.")
        return value
    
    def validate_compare_price(self, value):
        """Validate compare price is greater than price."""
        if value is not None and hasattr(self, 'initial_data'):
            price = self.initial_data.get('price')
            if price and value <= float(price):
                raise serializers.ValidationError(
                    "Compare price must be greater than regular price."
                )
        return value
    
    def validate_stock(self, value):
        """Validate stock is non-negative."""
        if value < 0:
            raise serializers.ValidationError("Stock cannot be negative.")
        return value


class ProductSearchSerializer(serializers.ModelSerializer):
    """
    Serializer for product search results.
    """
    category_name = serializers.CharField(source='category.name', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    average_rating = serializers.ReadOnlyField()
    review_count = serializers.ReadOnlyField()
    discount_percentage = serializers.ReadOnlyField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'title', 'slug', 'short_description', 'category_name',
            'brand_name', 'price', 'compare_price', 'primary_image',
            'average_rating', 'review_count', 'discount_percentage',
            'is_featured'
        ]
    
    def get_primary_image(self, obj):
        """Get primary product image URL."""
        primary_image = obj.images.filter(is_primary=True).first()
        if primary_image and primary_image.image:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(primary_image.image.url)
            return primary_image.image.url
        return None


class CategoryTreeSerializer(serializers.ModelSerializer):
    """
    Serializer for category tree structure.
    """
    children = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'children']
    
    def get_children(self, obj):
        """Get child categories recursively."""
        children = obj.children.filter(is_active=True)
        return CategoryTreeSerializer(children, many=True, context=self.context).data


class ProductStatsSerializer(serializers.Serializer):
    """
    Serializer for product statistics.
    """
    total_products = serializers.IntegerField()
    active_products = serializers.IntegerField()
    low_stock_products = serializers.IntegerField()
    out_of_stock_products = serializers.IntegerField()
    featured_products = serializers.IntegerField()
    total_categories = serializers.IntegerField()
    total_brands = serializers.IntegerField()


class BulkProductUpdateSerializer(serializers.Serializer):
    """
    Serializer for bulk product updates.
    """
    product_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1
    )
    updates = serializers.DictField()
    
    def validate_updates(self, value):
        """Validate update fields."""
        allowed_fields = [
            'status', 'is_featured', 'category', 'brand', 'price',
            'stock', 'tags'
        ]
        
        for field in value.keys():
            if field not in allowed_fields:
                raise serializers.ValidationError(
                    f"Field '{field}' is not allowed for bulk updates."
                )
        
        return value
