from django.contrib import admin
from .models import FamilyList, FamilyImage, Administrator, MonthlyAmount, Payment, EmailCredential

# Register your models here.
admin.site.register(FamilyList)
admin.site.register(FamilyImage)
admin.site.register(Administrator)
admin.site.register(MonthlyAmount)
admin.site.register(Payment)
admin.site.register(EmailCredential)