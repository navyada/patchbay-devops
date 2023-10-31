from rest_framework import serializers, status
from django.utils import timezone
from django.core.exceptions import ValidationError, PermissionDenied
from core.models import (
    Listing,
    Category,
    Address,
    Saved,
    ListingReview,
    UserReview,
    Orders,
    ListingImage)


class CategorySerializer(serializers.ModelSerializer):
    """ Serializer for categories """
    class Meta:
        model = Category
        fields = ['id', 'name', 'parent_category']
        read_only_fields = ['id']

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'address_1', 'address_2', 'city', 'state', 'zip_code']
        read_only_fields = ['id']
class ListingSerializer(serializers.ModelSerializer):
    """Serializer for listings"""
    address = AddressSerializer()
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price_cents', 'address', 'image'
            ]
        read_only_fields = ['id']

    def _get_category(self, category, listing):
        """Handle getting categories as needed"""
        for cat in category:
            listing.category.add(cat)

    def create(self, validated_data):
        """Create a listing"""
        address_data = validated_data.pop('address', {})
        category = validated_data.pop('category', [])
        address, created = Address.objects.get_or_create(
                                            address_1=address_data['address_1'],
                                            city=address_data['city'],
                                            state=address_data['state'],
                                            zip_code=address_data['zip_code']
                                            )
        listing = Listing.objects.create(address=address, **validated_data)
        self._get_category(category, listing)
        return listing

    def update(self, instance, validated_data):
        """Update a listing"""
        address_data = validated_data.pop('address', None)
        if address_data:
            address, created = Address.objects.get_or_create(
                                address_1=address_data['address_1'],
                                city=address_data['city'],
                                state=address_data['state'],
                                zip_code=address_data['zip_code'])
            validated_data['address'] = address
        category = validated_data.pop('category', None)
        if category is not None:
            instance.category.clear()
            self._get_category(category, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class ListingDetailSerializer(ListingSerializer):
    """Serializer for listing details"""
    class Meta(ListingSerializer.Meta):
        fields=['id', 'title', 'price_cents','description',
                'year', 'make', 'model', 'replacement_value',
                'address', 'image', 'avg_stars', 'num_reviews',
                'category']

class SavedSerializer(serializers.ModelSerializer):
    """Serializer for Saved model"""

    class Meta:
        model = Saved
        fields = ['id', 'user', 'listing']
        read_only_fields = ['id']

class ListingReviewSerializer(serializers.ModelSerializer):
    """Serializer for listing reviews"""
    class Meta:
        model = ListingReview
        fields = ['id', 'user', 'listing', 'stars', 'text']
        read_only_fields = ['id']


class UserReviewSerializer(serializers.ModelSerializer):
    """Serializer for user reviews"""
    class Meta:
        model = UserReview
        fields = ['id', 'lender', 'renter', 'stars', 'text']
        read_only_fields = ['id']

class OrdersSerializer(serializers.ModelSerializer):
    """Serializer for orders"""

    class Meta:
        model = Orders
        fields = ['id', 'user', 'lender', 'listing',
                  'requested_date', 'start_date', 'end_date',
                  'status', 'lender_response', 'subtotal_price',
                  'created_at', 'updated_at']

    def create(self, validated_data):
        num_days_rented = (validated_data['end_date'] - validated_data['start_date']).days + 1
        subtotal_price = validated_data['listing'].price_cents * num_days_rented
        validated_data['subtotal_price'] = subtotal_price
        listing = validated_data['listing']
        validated_data['lender'] = listing.user
        if validated_data['user'] == validated_data['lender']:
            raise serializers.ValidationError("The user and the lender cannot be the same.", code=status.HTTP_400_BAD_REQUEST)
        # Create the Orders instance with the updated data
        order = Orders.objects.create(**validated_data)
        return order

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_at = timezone.now()
        instance.save()
        return instance

class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'listing', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}