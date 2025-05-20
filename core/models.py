from django.db import models
from django.contrib.auth.models import AbstractUser


# Create your models here.
class User(AbstractUser):
    phone = models.CharField(max_length=50, blank=False)


class TransactionRecord(models.Model):
    """
    A record of the transaction submitted by a user. A transaction is not
    complete until confirmed by both parties having submitted their own
    transaction record.
    """

    STATUS_CHOICES = (
        (0, "Pending"),
        (1, "Confirmed"),
        (2, "Rejected"),
    )

    creator_user = models.ForeignKey(
        "User", on_delete=models.CASCADE, related_name="transaction_records_creator"
    )
    target_user = models.ForeignKey(
        "User",
        on_delete=models.CASCADE,
        related_name="transaction_records_target",
    )
    status = models.IntegerField(choices=STATUS_CHOICES, default=0)
    # Is this transaction record submitted by the receiver of the payment?
    from_receiver = models.BooleanField()
    description = models.CharField(max_length=255)
    amount = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Transaction Record (by {self.creator_user}) {self.amount} from {self.provider} to {self.receiver} at {self.created_at}"

    @property
    def provider(self):
        """Returns the user who is the provider in the transaction."""
        return self.creator_user if not self.from_receiver else self.target_user

    @property
    def receiver(self):
        return self.creator_user if self.from_receiver else self.target_user

    # @property
    # def transaction_type(self):
    #     """The type of transaction relative to the user who created this record."""
    #     return "charge" if self.from_receiver else "payment"

    # @property
    # def targets_transaction_type(self):
    #     """The type of transaction relative to the target user."""
    #     return "payment" if self.from_receiver else "charge"


class Balance(models.Model):
    """A balance between two people."""
    # users
    users = models.ManyToManyField(
        "user", through="UserBalance", blank=True, related_name="balances"
    )
    amount = models.PositiveIntegerField(default=0)
    time_updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Balance of {self.amount} credited to {self.credited}, debt from {self.debted}"

    @property
    def credited(self):
        return self.userbalance_set.get(credited=True).user

    @property
    def debted(self):
        return self.userbalance_set.get(credited=False).user


class UserBalance(models.Model):
    """A join table to link User to one of their Balances."""

    user = models.ForeignKey("User", on_delete=models.CASCADE)
    balance = models.ForeignKey("Balance", on_delete=models.CASCADE)
    credited = models.BooleanField()

    @property
    def other_user(self):
        """Get the user on the other side of this balance."""
        return self.balance.users.exclude(id=self.user.id).get()

    # @property
    # def relative_value(self):
    #     value = self.balance.amount
    #     return self.balance.currency.value_of(value if self.credited else -value)

    @property
    def relative_value_repr(self):
        value = self.balance.amount
        return value if self.credited else -value