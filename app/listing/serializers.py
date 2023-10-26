from rest_framework import serializers
from core.models import (
    Listing)


class ListingSerializer(serializers.ModelSerializer):
    """Serializer for listings"""
    # tags = TagSerializer(many=True, required=False)
    class Meta:
        model = Listing
        fields = [
            'id', 'title', 'price_cents'
            ]
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create a listing"""
        # tags = validated_data.pop('tags', [])
        # ingredients = validated_data.pop('ingredients', [])
        listing = Listing.objects.create(**validated_data)
        # self._get_or_create_tags(tags, recipe)
        # self._get_or_create_ingredients(ingredients, recipe)
        return listing

    def update(self, instance, validated_data):
        """Update a listing"""
        # tags = validated_data.pop('tags', None)
        # ingredients = validated_data.pop('ingredients', None)
        # if tags is not None:
        #     instance.tags.clear()
        #     self._get_or_create_tags(tags, instance)
        # if ingredients is not None:
        #     instance.ingredients.clear()
        #     self._get_or_create_ingredients(ingredients, instance)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class ListingDetailSerializer(ListingSerializer):
    """Serializer for listing details"""
    class Meta(ListingSerializer.Meta):
        fields=['id', 'title', 'price_cents','description', 'year', 'make', 'model', 'replacement_value']
