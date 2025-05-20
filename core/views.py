from django.shortcuts import render, redirect
from django.views.generic import CreateView
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required
from django.db.models import BooleanField, Case, F, Q, When
from django.contrib import messages
from django.db import transaction
from .forms import SignUpForm, TransactionForm
from .models import TransactionRecord
from .utils import update_balance, get_balances

class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("core:home")
    template_name = "registration/signup.html"


@login_required
def home(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            amt = form.cleaned_data["amount"]
            desc = form.cleaned_data["description"]
            creator_user = request.user
            target_user = form.cleaned_data["to_user"]
            if creator_user == target_user:
                messages.error(
                    request, "You cannot transfer funds to your own account."
                )
                return redirect("core:home")
            from_receiver = request.POST["transaction_type"]  # submitted by receiver
            txn = TransactionRecord.objects.create(
                creator_user=creator_user,
                target_user=target_user,
                from_receiver=from_receiver,
                status=0,
                description=desc,
                amount=int(amt),
            )
            
            messages.success(request, f"Success! Payment success. id: {txn.id}")
            return redirect("core:home")

    else:
        form = TransactionForm()

    user = request.user
    latest_trans = (
        TransactionRecord.objects.filter(Q(creator_user=user) | Q(target_user=user))
        .select_related("creator_user", "target_user")
        .order_by("-created_at")[:5]
    )

    
    return render(
        request, "home.html", {"transaction_form": form, "transactions": latest_trans,
            "balances":get_balances(request.user)}
    )


@login_required
def transaction_confirm(request, trans_record_id):
    """Confirm a transaction record from another user."""
    txn = TransactionRecord.objects.get(id=trans_record_id)
    if txn.status == 0:
        if txn.target_user == request.user:
            txn.status = 1
            txn.save(update_fields=["status"])
            update_balance(txn)
            messages.success(request, "Transaction confirmed.")
        else:
            messages.error(request, "You must be target user of txn.")
    else:        
        messages.error(request, "Transaction is already submitted")
    return redirect("core:home")


