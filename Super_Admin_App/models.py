from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PilImage
from django.core.exceptions import ValidationError

class FamilyList(models.Model):
    family_name = models.CharField(max_length=100)
    location = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100, null=True, blank=True)
    no_of_family_members = models.PositiveIntegerField()
    family_bio = models.TextField()
    is_sponsored = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Families List"
        ordering = ['-created_at']

    def __str__(self):
        return self.family_name
    
def validate_image(image):
    try:
        img = PilImage.open(image)
        img.verify()
    except Exception:
        raise ValidationError(_("The uploaded file is not a valid image."))
    
class FamilyImage(models.Model):
    family = models.ForeignKey(FamilyList, related_name='images', on_delete=models.CASCADE)
    photo = models.ImageField(upload_to='family_photos/', validators=[validate_image])

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

class MonthlyAmount(models.Model):
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name="Monthly Amount"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Monthly Amount"
        verbose_name_plural = "Monthly Amounts"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.amount} (Created: {self.created_at.strftime('%Y-%m-%d')})"
    
class Payment(models.Model):
    sponsor = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    family = models.ForeignKey(FamilyList, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['-payment_date']
        verbose_name_plural = 'Payments'

    def __str__(self):
        return f'{self.sponsor.email} - {self.family.family_name} - {self.family.location} - ${self.amount}'