import pycountry, hashlib
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from . import misc


class Block(models.Model):
    index = models.IntegerField()
    timestamp = models.DateTimeField(default=timezone.now)
    model = models.CharField(max_length=100)  # e.g., 'User', 'Exchange'
    object_id = models.PositiveIntegerField()
    operation = models.CharField(max_length=10, choices=[('CREATE', 'CREATE'), ('UPDATE', 'UPDATE'), ('DELETE', 'DELETE')])
    data = models.JSONField()  # serialized model data
    previous_hash = models.CharField(max_length=64)
    hash = models.CharField(max_length=64)

    def compute_hash(self):     
        value = f"{self.index}{self.timestamp}{self.model}{self.object_id}{self.operation}{self.previous_hash}" # skipped self.data
        return hashlib.sha256(value.encode()).hexdigest()
    
    def is_valid_chain(self):
        for i in range(1, Block.objects.count()):
            current = Block.objects.get(index=i)
            previous = Block.objects.get(index=i-1)
            if current.hash != current.compute_hash():
                print(f"Invalid hash at block {i}")
                return False
            if current.previous_hash != previous.hash:
                print(f"Invalid previous hash at block {i}")
                return False
        return True
    
class UserVerification(models.Model):
    verifier = models.ForeignKey("User", related_name="verifications_made", on_delete=models.CASCADE)
    candidate = models.ForeignKey("User", related_name="verifications_received", on_delete=models.CASCADE)
    trust_score = models.FloatField(default=0.1)  # 0 to 1, how much verifier trusts candidate
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("verifier", "candidate")  # can't verify same user twice

    def __str__(self):
        return f"{self.verifier.username} -> {self.candidate.username}"
    

class User(AbstractUser):
    exchange = models.ForeignKey(
        "Exchange", on_delete=models.SET_NULL, null=True, related_name="users"
    )
    phone = models.CharField(max_length=50, blank=False)
    government_id = models.CharField(max_length=50, blank=True)
    date_of_birth = models.DateField(help_text='Date of Birth in yyyy-mm-dd format.')
    balance = models.IntegerField(default=0)


class Exchange(models.Model):
    code = models.CharField(max_length=5, unique=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    country_city = models.CharField(max_length=6)
    postal_code = models.CharField(max_length=20, blank=True)
    # created_by = models.ForeignKey(
    #     "User", on_delete=models.SET_NULL, null=True, related_name="created_exchanges"
    # )

    def __str__(self):
        return f"{self.code}({self.name})"

    def get_country_and_subdivision(self):
        try:
            subdivision = pycountry.subdivisions.get(code=self.country_city)
            if subdivision:
                country = pycountry.countries.get(alpha_2=subdivision.country_code)
                return f'{subdivision.name},{country.name}'
        except Exception as e:
            print(f"Error: {e}")
        return self.country_city


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
    image = models.ImageField(upload_to='offering/%Y/%m/%d/', null=True, blank=True)
    # ResizedImageField(size=[500, 300],quality=25,upload_to="offering/%Y/%m/%d/",null=True,blank=True,)
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
    description = models.CharField(max_length=255, blank=True)
    amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now) #auto_now_add=True)

    def __str__(self):
        return f"{self.buyer} -> {self.seller}: {self.amount}"


# site specific
class GeneralSettings(models.Model):
    key = models.CharField(max_length=50)
    value = models.CharField(max_length=250)

    def __str__(self) -> str:
        return f"{self.key}:{self.value}"
