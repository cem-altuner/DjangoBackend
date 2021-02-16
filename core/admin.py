from django.contrib import admin
from .models import *
# Register your models here.
admin.site.register(Company)
admin.site.register(Product)
admin.site.register(Customer)
admin.site.register(ShoppingListItem)
admin.site.register(ShoppingList)
admin.site.register(Catalog)
