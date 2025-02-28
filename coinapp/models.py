from django.contrib.auth.models import AbstractUser
from django.db import models
from django_resized import ResizedImageField
from . import misc


class User(AbstractUser):
    exchange = models.ForeignKey("Exchange", on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=50, blank=False)
    amount = models.IntegerField(default=0)


class Exchange(models.Model):
    COUNTRY_CHOICES = misc.COUNTRIES
    code = models.CharField(max_length=5, unique=True)
    title = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    pending_users = models.ManyToManyField("User", related_name="pending_exchange")
    country = models.CharField(max_length=2, choices=COUNTRY_CHOICES)
    admin = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="exchange_admin"
    )

    def __str__(self):
        return f"{self.code}({self.title})"


class Listing(models.Model):
    CATEGORY_CHOICES = misc.CATEGORIES
    LISTING_CHOICES = [
        ("O", "Offering"),
        ("W", "Wants"),
    ]
    user = models.ForeignKey("User", on_delete=models.CASCADE)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    heading = models.CharField(max_length=255)
    detail = models.TextField()
    rate = models.CharField(max_length=100, blank=True)
    listing_type = models.CharField(max_length=1, choices=LISTING_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)
    img = ResizedImageField(
        size=[500, 300],
        quality=25,
        upload_to="offering/%Y/%m/%d/",
        null=True,
        blank=True,
    )

    # models.ImageField(upload_to='offering/%Y/%m/%d/', null=True, blank=True)
    def __str__(self):
        return f"{self.heading}({self.detail[:30]}...)"


class Transaction(models.Model):
    seller = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="txn_seller"
    )
    buyer = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="txn_buyer"
    )
    listing = models.ForeignKey("Listing", on_delete=models.SET_NULL, null=True)
    description = models.CharField(max_length=255)
    amount = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} -> {self.seller}: {self.amount}"


# site specific
class GeneralSettings(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f"{self.key}:{self.value}"
