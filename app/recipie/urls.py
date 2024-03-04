"""URL mappings for the recipie APP"""
from django.urls import path,include 
from rest_framework.routers import DefaultRouter
from recipie import views 

router=DefaultRouter()
router.register('recipies',views.RecipieViewSet)
router.register('tags',views.TagViewSet)
router.register('ingredients',views.IngredientViewSet)
app_name='recipie'

urlpatterns = [
    path('',include(router.urls)),
]
