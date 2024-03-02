from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from core import models 
# Register your models here.

class UserAdmin(BaseUserAdmin):
    ordering=['id']
    list_display=['email','name']
    fieldsets=(
        (None,{'fields':['name','email','password']}),
        (
            _('Permissions'),
            {
                'fields': (
                    'is_active',
                    'is_staff',
                    'is_superuser'
                )
            }   
        ),
        (_('Important dates for Maharani Pillu'),{'fields':('last_login',)}),
    )
    readonly_fields=['last_login']
    add_fieldsets=(
        (None,{
            'classes':('wide',),
            'fields':(
                'email',
                'password1',
                'password2',
                'name',
                'is_active',
                'is_staff',
                'is_superuser',
            )
        }),
    )
    
class RecipieAdmin(admin.ModelAdmin):
    list_display = ('title','description','price')   
    list_filter = ('title','description','price')  

class TagAdmin(admin.ModelAdmin):
    list_display=('name',)
    list_filter=('name',)

admin.site.register(models.User,UserAdmin)
admin.site.register(models.Recipie,RecipieAdmin)
admin.site.register(models.Tag,TagAdmin)