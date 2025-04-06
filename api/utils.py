from django.db.models import BooleanField, Case, F, Q, When
from django.db import transaction
from django.conf import settings
from coinapp.models import Transaction


def get_transaction_queryset(user):
    return (
        Transaction.objects.filter(Q(seller=user) | Q(buyer=user))
        .select_related("seller", "buyer")
        .annotate(
            is_received=Case(
                When(Q(seller=user), then=True),
                default=False,
                output_field=BooleanField(),
            )
        )
        .order_by("-created_at")
    )

def save_transaction(transaction_type,amt,desc,seller, buyer):    
    if seller == buyer:
        msg = "You cannot send money to you own account"
        return {'success':False,'msg':msg,'txn_obj':None}
    if transaction_type == "buyer":
        # send money
        seller, buyer = buyer, seller

    # _check_max_min_balance
    if seller.balance+amt > settings.MAXIMUM_BALANCE:
        return {'success':False,'msg':"Seller reached Maximum balance",'txn_obj':None}
    if buyer.balance-amt < settings.MINIMUM_BALANCE:
        return {'success':False,'msg':"Buyer reached Minimum balance",'txn_obj':None}
    
    with transaction.atomic():
        seller.balance = F("balance") + amt
        buyer.balance = F("balance") - amt
        seller.save(update_fields=["balance"])
        buyer.save(update_fields=["balance"])
        txn = Transaction.objects.create(
            seller=seller,
            buyer=buyer,
            description=desc,
            amount=amt,
        )
        return {'success':True,'msg':'','txn_obj':txn}
    return {'success':False,'msg':"Transaction Failed",'txn_obj':None}
