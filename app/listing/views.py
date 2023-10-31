"""
Views for the Listing APIs
"""
from drf_spectacular.utils import (
    extend_schema_view,
    extend_schema,
    OpenApiParameter,
    OpenApiTypes
)
from rest_framework import (viewsets, mixins, status)

from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q


from core.models import (
    User,
    Listing,
    Category,
    Saved,
    ListingReview,
    Orders,
    UserReview,
    ListingImage)
from listing import serializers
from rest_framework import status

class ListingViewSet(viewsets.ModelViewSet):
    """View for manage listing APIs (user's listings, not all)"""
    serializer_class = serializers.ListingDetailSerializer
    queryset = Listing.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
            """Retrive listings for authenticated user"""
            categories = self.request.query_params.get('category')
            queryset = self.queryset
            if categories:
                cat_ids = self._params_to_ints(categories)
                queryset = queryset.filter(category__id__in=cat_ids)
            if self.request.user.is_staff:
                return queryset.order_by('-id').distinct()
            return queryset.filter(user=self.request.user).order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ListingSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new listing"""
        serializer.save(user=self.request.user)


class ListingImageViewSet(viewsets.ModelViewSet):
    """Viewset for listing images"""
    serializer_class = serializers.ListingImageSerializer
    queryset = ListingImage.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        """Retrieve images for listing in question"""
        listing_id = self.request.query_params.get('listing')
        if listing_id:
            return self.queryset.filter(listing=listing_id).order_by('-id')
        return self.queryset.none()

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to listing"""
        listing_id = self.request.query_params.get('listing')
        if not listing_id:
            return Response(
                            {'detail': 'Please provide a listing ID in the query parameters.'},
                            status=status.HTTP_400_BAD_REQUEST
                            )
        try:
            listing = Listing.objects.get(id=listing_id)
        except Listing.DoesNotExist:
            return Response({'detail': 'Listing not found.'}, status=status.HTTP_404_NOT_FOUND)
        owner = listing.user
        if self.request.user != owner:
            return Response(
                    {'detail': 'User does not have permission to upload images to this listing.'},
                    status=status.HTTP_400_BAD_REQUEST
                    )
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            serializer.save(listing=listing)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ListingReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for viewing all listings.
    """
    queryset = Listing.objects.all()
    serializer_class = serializers.ListingDetailSerializer
    def _params_to_ints(self, qs):
        """Convert strings to integers"""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrive listings for authenticated user"""
        categories = self.request.query_params.get('category')
        queryset = self.queryset
        if categories:
            cat_ids = self._params_to_ints(categories)
            queryset = queryset.filter(category__id__in=cat_ids)
        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ListingSerializer
        return self.serializer_class


class CategoryViewSet(viewsets.ModelViewSet):
    """Admin auth required to post, patch, and delete"""
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAdminUser]



class CategoryReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """
    A simple ViewSet for only viewing categories.
    """
    queryset = Category.objects.all()
    serializer_class = serializers.CategorySerializer

class SavedViewSet(viewsets.ModelViewSet):
    """A viewset for saving listings"""
    serializer_class = serializers.SavedSerializer
    queryset = Saved.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrive listings for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id').distinct()

class ListingReviewViewSet(viewsets.ModelViewSet):
    """A viewset for listing reviews"""
    serializer_class = serializers.ListingReviewSerializer
    queryset = ListingReview.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        """Retrive reviews for authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-id').distinct()

    def create(self, request, *args, **kwargs):
        listing_id = request.data.get('listing')
        try:
            listing = Listing.objects.get(pk=listing_id)
        except Listing.DoesNotExist:
            return Response({"error": "Listing not found"}, status=status.HTTP_404_NOT_FOUND)

        if listing.user == request.user:
            return Response({"error": "You cannot review your own listing"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            order = Orders.objects.get(user=self.request.user, listing=listing, status='Approved')
        except Orders.DoesNotExist:
            return Response({"error": "User can only review listings they have ordered"}, status=status.HTTP_400_BAD_REQUEST)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class ListingReviewReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset for listing reviews without authentication"""
    serializer_class = serializers.ListingReviewSerializer
    queryset = ListingReview.objects.all()


class UserReviewViewSet(viewsets.ModelViewSet):
    """A viewset for listing user reviews"""
    serializer_class = serializers.UserReviewSerializer
    queryset = UserReview.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        """Retrive reviews for authenticated user"""
        return self.queryset.filter(lender=self.request.user).order_by('-id').distinct()

    def create(self, request, *args, **kwargs):
        renter_id = request.data.get('renter')
        lender_id = request.data.get('lender')
        try:
            order = Orders.objects.get(lender=lender_id)
        except Orders.DoesNotExist:
            return Response({"error": "Order not found"}, status=status.HTTP_404_NOT_FOUND)

        if lender_id == renter_id:
            return Response({"error": "You cannot review yourself"}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
class UserReviewReadOnlyViewSet(viewsets.ReadOnlyModelViewSet):
    """A viewset for user reviews without authentication"""
    serializer_class = serializers.UserReviewSerializer
    queryset = UserReview.objects.all()

class OrdersViewSet(viewsets.ModelViewSet):
    """A viewset for listing orders"""
    serializer_class = serializers.OrdersSerializer
    queryset = Orders.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    def get_queryset(self):
        """Retrive orders for authenticated user"""
        return self.queryset.filter(Q(user=self.request.user) | Q(lender=self.request.user)).order_by('-id').distinct()

    def destroy(self, request, *args, **kwargs):
        if not request.user.is_staff:
            raise serializers.PermissionDenied("You do not have permission to delete this order.")
        return super(OrdersViewSet, self).destroy(request, *args, **kwargs)