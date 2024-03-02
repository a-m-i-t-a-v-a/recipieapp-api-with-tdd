"""Serializers for recipie apis"""
from rest_framework import serializers
from core.models import Recipie,Tag 

class TagSerializer(serializers.ModelSerializer):
    """Serializer for tags"""
    class Meta:
        model=Tag 
        fields=['id','name']
        read_only_fields=['id']
class RecipieSerializer(serializers.ModelSerializer):
    """Serializer for recipies"""
    tags=TagSerializer(many=True,required=False)
    class Meta:
        model=Recipie
        fields=['id','title','time_minutes','price','link','tags']
        read_only_fields=['id']
        
    def create(self,validated_data):
        """Create a recipie"""
        tags=validated_data.pop('tags',[])
        recipie=Recipie.objects.create(**validated_data)
        auth_user=self.context['request'].user 
        for tag in tags:
            tag_obj,created=Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipie.tags.add(tag_obj)
            
        return recipie
        
class RecipieDetailSerializer(RecipieSerializer):
    class Meta(RecipieSerializer.Meta):
        fields=RecipieSerializer.Meta.fields+['description']
        

        