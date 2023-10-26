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
    Listing)
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
        """Retrive all listings"""
        if self.request.user.is_staff:
            return self.queryset.order_by('-id').distinct()
        return self.queryset.filter(user=self.request.user).order_by('-id').distinct()

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
    A simple ViewSet for only viewing listings.
    """
    queryset = Listing.objects.all()
    serializer_class = serializers.ListingDetailSerializer

