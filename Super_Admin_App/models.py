from django.db import models
from django.contrib.auth.models import User

class FamilyList(models.Model):
    family_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100)
    no_of_family_members = models.PositiveIntegerField()
    family_bio = models.TextField()
    is_sponsored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Families List"
        ordering = ['-created_at']

    def __str__(self):
        return self.family_name
    
class FamilyImage(models.Model):
    family = models.ForeignKey(FamilyList, related_name='images', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='family_photos/')

    def __str__(self):
        return f"{self.family.family_name} - photo"
    
class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_photo = models.ImageField(upload_to = 'admin_media')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = 'Adminstrators'

    def __str__(self):
        return f'{self.user.email}'