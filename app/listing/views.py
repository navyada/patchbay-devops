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

from core.models import (
    Listing,
    Category,
    Saved)
from listing import serializers

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
        # elif self.action == 'upload_image':
        #     return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new listing"""
        serializer.save(user=self.request.user)

    # @action(methods=['POST'], detail=True, url_path='upload-image')
    # def upload_image(self, request, pk=None):
    #     """Upload an image to recipe"""
    #     recipe = self.get_object()
    #     serializer = self.get_serializer(recipe, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
        return queryset.filter().order_by('-id').distinct()

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.ListingSerializer


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