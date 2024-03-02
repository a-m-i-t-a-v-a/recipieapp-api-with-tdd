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
        
    def _get_or_create_tags(self,tags,recipie):
        """Handle getting or creating tags as needed"""
        auth_user=self.context['request'].user 
        for tag in tags:
            tag_obj,created=Tag.objects.get_or_create(
                user=auth_user,
                **tag,
            )
            recipie.tags.add(tag_obj)
        
    def create(self,validated_data):
        """Create a recipie"""
        tags=validated_data.pop('tags',[])
        recipie=Recipie.objects.create(**validated_data)
        self._get_or_create_tags(tags,recipie)
        return recipie
    
    def update(self,instance,validated_data):
        """Update recipie"""
        tags=validated_data.pop('tags',None)
        if tags is not None:
            instance.tags.clear()
            self._get_or_create_tags(tags,instance)
        for attr,value in validated_data.items():
            setattr(instance,attr,value)
        instance.save()
        return instance
        
class RecipieDetailSerializer(RecipieSerializer):
    class Meta(RecipieSerializer.Meta):
        fields=RecipieSerializer.Meta.fields+['description']
        

        