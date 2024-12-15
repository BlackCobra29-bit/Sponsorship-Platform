from django.db import models
from django.contrib.auth.models import User
from phonenumber_field.modelfields import PhoneNumberField
from django_countries.fields import CountryField
from Super_Admin_App.models import FamilyList

class SponosrAccount(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone_number = PhoneNumberField(blank=True, null=True)
    location = CountryField()
    sponsor_photo = models.ImageField(upload_to = 'sponsor_media')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = 'Sponsors Account'

    def __str__(self):
        return f'{self.user.email}'

class SponsorFamilyRelation(models.Model):
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sponsored_families')
    family = models.ForeignKey(FamilyList, on_delete=models.CASCADE, related_name='sponsor')
    sponsored_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Sponsor Family Relations"
        unique_together = ('sponsor', 'family')
        ordering = ['-sponsored_at']

    def __str__(self):
        return f"{self.sponsor.first_name} {self.sponsor.last_name} sponsors {self.family.family_name}"
