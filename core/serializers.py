from rest_framework import serializers
from .models import *
from .models import Customer as User
#from rest_email_auth.serializers import RegistrationSerializer
"""
class MyRegistrationSerializer(RegistrationSerializer):

    class Meta:
        # You must include the 'email' field for the serializer to work.
        fields = (
            'email',
            'password',
        )
        model = User
"""


class CompanySerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Company
        fields = ['id', 'name', 'country', 'city','logo']

    def get_logo(self, obj):
        request = self.context.get('request')
        photo_url = obj.logo.url
        return request.build_absolute_uri(photo_url).replace('/api','').replace('/companies','')



# Serializers define the API representation.
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email', 'password']


class CatalogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Catalog
        fields = ['id', 'name', 'company', 'pdf_file']


class ShoppingListItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingListItem
        fields = ['id', 'shopping_list', 'text',
                  'is_visible', 'company', 'is_checked']


class ShoppingListSerializer(serializers.ModelSerializer):
    shopping_list_items = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = ShoppingList
        fields = ['id', 'name', 'is_deleted_offline', 'customer', 'shopping_list_items', ]
        ordering = ['-id']

    def get_shopping_list_items(self, obj):
        request = self.context['request']
        cur_sl_items = ShoppingListItem.objects.filter(
            shopping_list=obj.id).order_by('-id')
        rv = []
        for item in cur_sl_items:
            serialized_item = ShoppingListItemSerializer(item)
            rv.append(serialized_item.data)
        return rv

