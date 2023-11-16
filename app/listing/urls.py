"""URL mappings for the listing app"""

from django.urls import path, include

from rest_framework.routers import DefaultRouter

from listing import views

router = DefaultRouter()
router.register('listings',
                views.ListingViewSet)
router.register('readonly',
                views.ListingReadOnlyViewSet,
                basename='listingreadonly')
router.register('category',
                views.CategoryViewSet)
router.register('categoryreadonly',
                views.CategoryReadOnlyViewSet,
                basename='categoryreadonly')
router.register('saved',
                views.SavedViewSet)
router.register('listingreview',
                views.ListingReviewViewSet)
router.register('listingreviewreadonly',
                views.ListingReviewReadOnlyViewSet,
                basename='listingreviewreadonly')
router.register('orders',
                views.OrdersViewSet,
                basename='orders')
router.register('userreview',
                views.UserReviewViewSet,
                basename='userreview')
router.register('userreviewreadonly',
                views.UserReviewReadOnlyViewSet,
                basename='userreviewreadonly')
router.register('upload-image',
                views.ListingImageViewSet,
                basename='uploadimage')
app_name = 'listing'
urlpatterns = [path("", include(router.urls))]
