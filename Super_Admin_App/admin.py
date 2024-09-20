from django.contrib import admin
from .models import FamilyList, FamilyImage, Administrator

# Register your models here.
admin.site.register(FamilyList)
admin.site.register(FamilyImage)
admin.site.register(Administrator)