from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField
from . import misc


class User(AbstractUser):
    exchange = models.ForeignKey(
        "Exchange", on_delete=models.SET_NULL, null=True, related_name="users"
    )
    government_id = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(help_text='Date of Birth in yyyy-mm-dd format.')
    balance = models.IntegerField(default=0)


class Exchange(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    country_city = models.CharField(max_length=6)
    postal_code = models.CharField(max_length=20, blank=True)
    created_by = models.ForeignKey(
        "User", on_delete=models.SET_NULL, null=True, related_name="created_exchanges"
    )

    def __str__(self):
        return f"{self.code}({self.name})"


class Listing(models.Model):
    CATEGORY_CHOICES = misc.CATEGORIES
    LISTING_CHOICES = [("O", "Offering"), ("W", "Wants"),]
    user = models.ForeignKey("User", on_delete=models.CASCADE, related_name="listings")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()
    rate = models.CharField(max_length=100, blank=True)
    listing_type = models.CharField(max_length=1, choices=LISTING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    image = ResizedImageField(
        size=[500, 300],
        quality=25,
        upload_to="offering/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    # models.ImageField(upload_to='offering/%Y/%m/%d/', null=True, blank=True)
    def __str__(self):
        return f"{self.title}({self.description[:30]}...)"


class Transaction(models.Model):
    seller = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="txn_seller"
    )
    buyer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="txn_buyer"
    )
    listing = models.ForeignKey(
        Listing, on_delete=models.SET_NULL, null=True, related_name="transactions"
    )
    description = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} -> {self.seller}: {self.amount}"


# site specific
class GeneralSettings(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f"{self.key}:{self.value}"
