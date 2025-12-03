from stellar_sdk import Asset, Keypair, Network, Server,CreateAccount, TransactionBuilder

from django.db.models import BooleanField, Case, F, Q, When
from django.db import transaction
from django.conf import settings
from rest_framework.throttling import SimpleRateThrottle
from coinapp.models import Transaction

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

class StellarPayment:
    """
        1. Issuer Account (mints tokens)
            + Creates the LETS asset (e.g., LETS:GBLAHISSUER...)
            + Can mint unlimited new LETS
            + Cannot hold its own asset
        
        2. Treasury / Distributor Account
            + Holds the initial supply
            + Distributes tokens to users
            + Burns tokens (by sending back to issuer)
        
        3. User Accounts
            + Hold LETS tokens
            + Cannot mint tokens
    """
    def __init__(self,asset_code):
        self.server = Server(horizon_url="https://horizon-testnet.stellar.org")
        self.network = Network.TESTNET_NETWORK_PASSPHRASE
        # Issuer Public Key: GBCYEL4PJNMANBYVQHDBOHMMP5ZFEOMW2OOAKMRD4JNGEQXPPNWGQEVP
        self.issuer = Keypair.from_secret(settings.STELLAR_ISSUER_SECRET) 
        # Distributor Public Key: GADFBSAUXPNYO77QMLXBBI2RPTIURLXPNHCC5DEIJYKBCWDH7ECJJSSC
        self.distributor = Keypair.from_secret(settings.STELLAR_DISTRIBUTOR_SECRET)  
        self.asset = Asset(asset_code, self.issuer.public_key)

    def _get_txn_builder(self, source_public_key):
        source_account = self.server.load_account(source_public_key)
        return TransactionBuilder(source_account=source_account,network_passphrase=self.network,base_fee=100)

    def _submit_txn(self,txn,source_keypair):    
        txn.sign(source_keypair)    
        return self.server.submit_transaction(txn)

    def create_ac(self,destination_keypair):        
        source_keypair = self.issuer
        ac_txn = self._get_txn_builder(source_keypair.public_key)
        txn = ac_txn.append_operation(CreateAccount(destination=destination_keypair.public_key,
            starting_balance="10",)).set_timeout(100).build()
        txn_resp = self._submit_txn(txn,source_keypair)

    def change_trust(self,source_keypair,limit="1000000"):
        trust_txn = self._get_txn_builder(source_keypair.public_key)
        txn = trust_txn.append_change_trust_op(asset=self.asset).set_timeout(100).build()
        trust_txn_resp = self._submit_txn(txn,source_keypair)
    
    def payment(self,destination_public, amount,distributor_funding=False):
        if distributor_funding:
            # if funding the distributor
            source_keypair = self.issuer
        else:
            source_keypair = self.distributor
        payment_txn = self._get_txn_builder(source_keypair.public_key)
        txn = payment_txn.append_payment_op(destination=destination_public,asset=self.asset,amount=amount).set_timeout(100).build()
        payment_txn_resp = self._submit_txn(txn,source_keypair)

    def fund_distributor(self):
        self.change_trust(self.distributor)
        self.payment(self.distributor.public_key,1_00_000,distributor_funding=True)

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

    try:
        amt = int(amt)
    except ValueError:
        # if . in amt
        return resp(False, "Txn Amount must be Integer.")
    if amt < 1:
        return resp(False, "Txn Amount must be greater than 0.")
    
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
