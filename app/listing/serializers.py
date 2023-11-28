from rest_framework import serializers, status
from django.utils import timezone
from core.models import (
    Listing,
    Category,
    Address,
    Saved,
    ListingReview,
    UserReview,
    Orders,
    ListingImage,
    UnavailableDate,
    )
from datetime import timedelta


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


class UnavailableDateSerializer(serializers.ModelSerializer):
    """Serializer for unavailable dates"""
    class Meta:
        model = UnavailableDate
        fields = '__all__'


class ListingDetailSerializer(serializers.ModelSerializer):
    """Serializer for listing details"""
    address = AddressSerializer()
    unavailable_dates = UnavailableDateSerializer(many=True, required=False)
    category = CategorySerializer(many=True, required=False)

    class Meta:
        model = Listing
        fields = [
                    'id', 'title', 'price_cents', 'description',
                    'year', 'make', 'model', 'replacement_value_cents',
                    'address', 'avg_stars', 'num_reviews',
                    'category', 'unavailable_dates']
        read_only_fields = ['id', 'avg_stars', 'num_reviews']

    def _get_or_create_address(self, address_data):
        address, created = Address.objects \
            .get_or_create(
                            address_1=address_data['address_1'],
                            city=address_data['city'],
                            state=address_data['state'],
                            zip_code=address_data['zip_code']
                            )
        return address

    def _get_category(self, category, listing):
        """Handle getting categories as needed"""
        for category_data in category:
            cat = Category.objects.get(**category_data)
            listing.category.add(cat)

    def _get_dates(self, unavailable_dates, listing):
        for date_data in unavailable_dates:
            date, _ = UnavailableDate.objects.get_or_create(**date_data)
            if date not in listing.unavailable_dates.all():
                listing.unavailable_dates.add(date)

    def create(self, validated_data):
        """Create a listing"""
        address_data = validated_data.pop('address', {})
        category = validated_data.pop('category', [])
        unavailable_dates_data = validated_data.pop('unavailable_dates', [])
        address = self._get_or_create_address(address_data)
        listing = Listing.objects.create(address=address, **validated_data)
        self._get_category(category, listing)
        self._get_dates(unavailable_dates_data, listing)
        return listing

    def update(self, instance, validated_data):
        """Update a listing"""
        address_data = validated_data.pop('address', None)
        if address_data:
            address = self._get_or_create_address(address_data)
            validated_data['address'] = address
        category = validated_data.pop('category', None)
        if category is not None:
            instance.category.clear()
            self._get_category(category, instance)
        unavailable_dates_data = validated_data.pop('unavailable_dates', None)
        if unavailable_dates_data is not None:
            instance.unavailable_dates.clear()
            self._get_dates(unavailable_dates_data, instance)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class ListingSerializer(ListingDetailSerializer):
    """Serializer for listings"""
    studio = serializers.CharField(source='user.studio', read_only=True)
    class Meta(ListingDetailSerializer.Meta):
        fields = [
            'id', 'title', 'studio', 'price_cents', 'address', 'image'
            ]


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
        read_only_fields = ['id', 'subtotal_price', 'lender']

    def create(self, validated_data):
        num_days_rented = (
                            validated_data['end_date'] -
                            validated_data['start_date']).days + 1
        subtotal_price = validated_data['listing'].price_cents \
            * num_days_rented
        validated_data['subtotal_price'] = subtotal_price
        listing = validated_data['listing']
        validated_data['lender'] = listing.user
        if validated_data['user'] == validated_data['lender']:
            raise serializers.ValidationError(
                                                "The user and the \
                                                lender cannot be the same.",
                                                code=status.
                                                HTTP_400_BAD_REQUEST)
        start_date = validated_data.get('start_date')
        end_date = validated_data.get('end_date')
        listing = validated_data.get('listing')

        # Get a list of unavailable dates for the listing
        unavailable_dates = listing \
            .unavailable_dates \
            .values_list('date', flat=True)
        dates_between = [start_date + timedelta(days=x)
                         for x in range((end_date - start_date).days + 1)]
        unavailable_dates_set = set(unavailable_dates)
        overlapping_dates = [date for date in dates_between
                             if date in unavailable_dates_set]

        if overlapping_dates:
            raise serializers.ValidationError("The selected dates \
                                              are unavailable for the listing")

        order = Orders.objects.create(**validated_data)
        return order

    def update(self, instance, validated_data):
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        if 'status' in validated_data:
            if validated_data['status'] == 'Approved':
                dates_between = [
                                    instance.start_date + timedelta(days=x)
                                    for x in range(
                                                    (
                                                        instance.end_date -
                                                        instance.start_date)
                                                    .days + 1)]
                for date_data in dates_between:
                    date, _ = UnavailableDate.objects \
                        .get_or_create(date=date_data)
                    if date not in instance.listing.unavailable_dates.all():
                        instance.listing.unavailable_dates.add(date)
        instance.updated_at = timezone.now()
        instance.save()
        return instance


class ListingImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ListingImage
        fields = ['id', 'listing', 'image']
        read_only_fields = ['id']
        extra_kwargs = {'image': {'required': True}}
