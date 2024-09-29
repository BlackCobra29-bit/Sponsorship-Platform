from django.contrib import admin
from .models import FamilyList, FamilyImage, Administrator, MonthlyAmount

# Register your models here.
admin.site.register(FamilyList)
admin.site.register(FamilyImage)
admin.site.register(Administrator)
admin.site.register(MonthlyAmount)