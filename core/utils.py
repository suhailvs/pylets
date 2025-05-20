
from .models import Balance, UserBalance
def get_balance(usera, userb):
    """Load a balance between two users."""
    return (
        UserBalance.objects.select_related("balance")
        .get(user=usera, balance__users=userb)
        .balance
    )

def get_balances(user, include_balanced=False, credited=None):
    """Get the list of balances for a user. Filter out any where the value is
    back to 0.
    """
    q = UserBalance.objects.filter(user=user)
    if not include_balanced:
        q = q.exclude(balance__amount=0)
    if credited is not None:
        q = q.filter(credited=credited)
    return q

def update_balance(txn):

    """Update or create a balance between two users for a currency. Should be
    called from a method that was already created a transfer.
    """
    try:
        balance = get_balance(txn.provider, txn.receiver)
    except UserBalance.DoesNotExist:
        return new_balance(txn)#txn.provider, txn.receiver)

    # Establish the direction of the transfer
    if txn.provider == balance.debted:
        balance.amount += txn.amount
        balance.save()
        return balance

    balance.amount -= txn.amount
    if (balance.amount) < 0:
        balance.amount = abs(balance.amount)
        for userbalance in balance.userbalance_set.all():
            userbalance.credited = not userbalance.credited
            userbalance.save()

    balance.save()
    # TODO: does this cascade to the userbalance ?
    return balance


# TODO: tests
def new_balance(txn):
    balance = Balance(amount=txn.amount)
    balance.save()
    userbalancea = UserBalance(
        user=txn.provider, credited=False, balance=balance
    )
    userbalanceb = UserBalance(
        user=txn.receiver, credited=True, balance=balance
    )
    userbalancea.save()
    userbalanceb.save()
    balance.save()
    return balance