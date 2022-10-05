from django.contrib import admin
from .models import Inventory, InventoryGroup, Store

admin.site.register((Inventory, InventoryGroup, Store))
