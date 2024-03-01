"""Serializers for recipie apis"""
from rest_framework import serializers
from core.models import Recipie

class RecipieSerializer(serializers.ModelSerializer):
    """Serializer for recipies"""
    class Meta:
        model=Recipie
        fields=['id','title','time_minutes','price','link']
        read_only_fields=['id']
        
class RecipieDetailSerializer(RecipieSerializer):
    class Meta(RecipieSerializer.Meta):
        fields=RecipieSerializer.Meta.fields+['description']
        