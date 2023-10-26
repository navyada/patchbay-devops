from rest_framework import serializers
from core.models import (
    Listing,
    Category,
    Address,
    Saved)


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
            'id', 'title', 'price_cents', 'address'
            ]
        read_only_fields = ['id']


    def create(self, validated_data):
        """Create a listing"""
        address_data = validated_data.pop('address', {})  # Remove address data from validated_data
        address, created = Address.objects.get_or_create(
                                            address_1=address_data['address_1'],
                                            city=address_data['city'],
                                            state=address_data['state'],
                                            zip_code=address_data['zip_code']
                                            )
        listing = Listing.objects.create(address=address, **validated_data)
        return listing

    def update(self, instance, validated_data):
        """Update a listing"""
        address_data = validated_data.pop('address', {})
        if address_data:
            address, created = Address.objects.get_or_create(
                                address_1=address_data['address_1'],
                                city=address_data['city'],
                                state=address_data['state'],
                                zip_code=address_data['zip_code'])
            validated_data['address'] = address
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ListingDetailSerializer(ListingSerializer):
    """Serializer for listing details"""
    class Meta(ListingSerializer.Meta):
        fields=['id', 'title', 'price_cents','description', 'year', 'make', 'model', 'replacement_value','address']

class SavedSerializer(serializers.ModelSerializer):
    """Serializer for Saved model"""

    class Meta:
        model = Saved
        fields = ['id', 'user', 'listing']
        read_only_fields = ['id']