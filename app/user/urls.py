"""URL mappings for the user API"""

from django.urls import path, include
from user import views
from rest_framework.routers import DefaultRouter


router = DefaultRouter()
router.register('upload', views.UserImageUploadViewSet, basename='upload')
app_name = 'user'
urlpatterns = [
    path('create/', views.CreateUserView.as_view(), name='create'),
    path('token/', views.CreateTokenView.as_view(), name='token'),
    path('me/', views.ManageUserView.as_view(), name='me'),
    path("", include(router.urls))
]
