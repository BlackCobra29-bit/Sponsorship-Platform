from django.db import models
from django.contrib.auth.models import User
from PIL import Image as PilImage
from django.utils import timezone
from django.core.exceptions import ValidationError

class FamilyList(models.Model):
    family_name = models.CharField(max_length=100)
    Gender_Choices = [
        ('Male', 'Male'),
        ('Female', 'Female'),
        ('Unknown', 'Unknown'),
    ]
    gender = models.CharField(max_length=255, choices=Gender_Choices, null=True, blank=True)
    location = models.CharField(max_length=100)
    contact_address = models.CharField(max_length=100, null=True, blank=True)
    bank_account = models.CharField(max_length=255, null=True, blank=True)
    family_bio = models.TextField(null=True, blank=True)
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
    photo = models.ImageField(upload_to='family_photos/', validators=[validate_image], blank=True)

    def __str__(self):
        return f"{self.family.family_name} - photo"
    
class Administrator(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    admin_photo = models.ImageField(upload_to = 'admin_media', blank=True)
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
        verbose_name="Monthly Amount", default="30.00"
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
    sponsor = models.ForeignKey(User, on_delete=models.SET_NULL, related_name="payments", null=True, blank=True)
    sponsor_name = models.CharField(max_length=255, blank=True)  # Stores sponsor's name
    family = models.ForeignKey(FamilyList, on_delete=models.SET_NULL, related_name="payments", null=True, blank=True)
    family_name = models.CharField(max_length=255, blank=True)  # Stores family's name
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    overdue_payment = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    is_seen = models.BooleanField(default=False)

    class Meta:
        ordering = ["-payment_date"]
        verbose_name_plural = "Payments"

    def save(self, *args, **kwargs):
        # Populate sponsor_name from User model
        if self.sponsor:
            self.sponsor_name = f"{self.sponsor.first_name} {self.sponsor.last_name}"

        # Populate family_name from FamilyList model
        if self.family:
            self.family_name = f"{self.family.family_name} - {self.family.location}"

        super().save(*args, **kwargs)

    def __str__(self):
        sponsor_name = self.sponsor_name or "Deleted Sponsor"
        family_name = self.family_name or "Deleted Family"
        return f"{sponsor_name}'s Payment for {family_name} - ${self.amount}"