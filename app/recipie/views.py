"""Views for recipie apis"""
from rest_framework import viewsets,mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from core.models import Recipie,Tag
from . import serializers

class RecipieViewSet(viewsets.ModelViewSet):
    """View for manage recipie APIs"""
    serializer_class=serializers.RecipieDetailSerializer
    queryset=Recipie.objects.all()
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        """Retrieve recipies for authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')
    
    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action=='list':
            return serializers.RecipieSerializer
        return self.serializer_class
    
    def perform_create(self,serializer):
        """Create a new recipie"""
        serializer.save(user=self.request.user)
        
class TagViewSet(mixins.UpdateModelMixin,mixins.DestroyModelMixin,mixins.ListModelMixin,viewsets.GenericViewSet):
    """Manage tags in the database"""
    serializer_class=serializers.TagSerializer
    queryset=Tag.objects.all()
    authentication_classes=[TokenAuthentication]
    permission_classes=[IsAuthenticated]
    
    def get_queryset(self):
        """Filter queryset to authenticated user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')