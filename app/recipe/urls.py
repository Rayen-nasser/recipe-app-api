"""
URL mapping for the recipe app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter

from recipe import views  # Correctly import views from the 'recipe' app

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet, basename='recipe')

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),  # Include the URLs from the router
]
