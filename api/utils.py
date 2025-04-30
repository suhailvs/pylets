import requests
from django.db.models import BooleanField, Case, F, Q, When
from django.db import transaction
from django.conf import settings
from coinapp.models import Transaction, Block

from rest_framework.throttling import SimpleRateThrottle

class UsernameRateThrottle(SimpleRateThrottle):
    scope = 'login'

    def get_cache_key(self, request, view):
        username = request.data.get('username')
        if not username:
            return None
        return self.cache_format % {
            'scope': self.scope,
            'ident': username.lower()
        }


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


def save_transaction(transaction_type, amt, desc, seller, buyer):
    resp = lambda s, msg, txn=None: {"success": s, "msg": msg, "txn_obj": txn}
    if seller == buyer:
        return resp(False, "You cannot transfer funds to your own account.")
    if seller.exchange_id != buyer.exchange_id:
        msg = "Oops! You can only send money to members of your own exchange."
        return resp(False, msg)

    if transaction_type == "buyer":
        # send money
        seller, buyer = buyer, seller

    amt = int(amt)
    # _check_max_min_balance
    if seller.balance + amt > settings.MAXIMUM_BALANCE:
        return resp(False, "Seller has reached the maximum allowed amount")
    if buyer.balance - amt < settings.MINIMUM_BALANCE:
        return resp(False, "Insufficient balance to complete the transaction.")

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
        return resp(True, "", txn)
    return resp(False, "Transaction Failed")

def broadcast(table, data, peers):
    last_block = Block.objects.last()
    data = {'data':data,'table':table,'block_time':f'{last_block.timestamp}','previous_block_hash':last_block.previous_hash}
    for peer in peers:        
        try:            
            response = requests.post(f"{peer}/api/v1/peer/receive/", json=data, timeout=1)
            print(response.json())
        except Exception as e:
            print(f"Failed to broadcast to {peer}: {e}")
            
def create_block(data,model_name, block_time=None,operation="CREATE"):        
    previous = Block.objects.last()
    block = Block.objects.create(
        index=(previous.index + 1) if previous else 0,
        model=model_name,
        object_id=data['id'],
        operation=operation,
        data=data,
        previous_hash=previous.hash if previous else "0",
    )
    if block_time: block.timestamp=block_time
    block.hash = block.compute_hash()
    block.save()