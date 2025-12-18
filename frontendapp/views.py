from django.contrib.auth import get_user_model
from django.views.generic import CreateView, ListView, DeleteView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.db.models import Q, F
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.http import JsonResponse

from coinapp.models import Listing, GeneralSettings, Exchange
from frontendapp.forms import (
    SignUpForm,
    SignUpFormWithoutExchange,
    TransactionForm,
    ExchangeForm,
    ListingForm,
    get_state_choices,
)
from api.utils import get_transaction_queryset, save_transaction, StellarPayment

User = get_user_model()


def about_view(request):
    about_count = GeneralSettings.objects.get(key="about")
    about_count.value = int(about_count.value) + 1
    about_count.save()
    return render(request, "about.html")

def stellar_txn(request):
    if request.method=='POST':
        amt = int(request.POST['amount'])
        user = request.user
        if user.balance < amt:return JsonResponse({"data": 'low balance'})
        SQ = StellarPayment(asset_code=user.exchange.code)
        if request.POST['action']=='mint':
            # mint token in stellar
            SQ.payment(user.stellar_publickey,amt)
            user.balance = F('balance') - amt
            user.save(update_fields=['balance'])
            # user.refresh_from_db()
        elif request.POST['action']=='burn':
            pass

    return JsonResponse({"data": 'success'})

def ajax_views(request, purpose):
    resp = ""
    if purpose == "get_cities":
        resp = get_state_choices(request.GET.get("country"))
    # elif purpose == "get_balance":
    #     # i think it is not used
    #     resp = User.objects.get(username=request.GET.get("username")).amount
    return JsonResponse({"data": resp})


class SignUpJoinView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("frontendapp:home")
    template_name = "registration/signup_join.html"


class SignUpNewView(CreateView):
    form_class = SignUpFormWithoutExchange
    # success_url = reverse_lazy("frontendapp:home")
    template_name = "registration/signup_new.html"

    def form_valid(self, form):
        ctx = self.get_context_data()
        exchange_form = ctx["exchange_form"]
        if exchange_form.is_valid() and form.is_valid():
            with transaction.atomic():
                exchange_obj = exchange_form.save()
                user_obj = form.save(exchange_obj=exchange_obj)
                login(self.request, user_obj)
                return redirect(reverse_lazy("frontendapp:home"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["exchange_form"] = ExchangeForm(self.request.POST)
        else:
            ctx["exchange_form"] = ExchangeForm()
        return ctx


@login_required
def transaction_view(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            amt = form.cleaned_data["amount"]
            desc = form.cleaned_data["description"]
            # default is seller transaction(receive money)
            seller = request.user
            buyer = form.cleaned_data["to_user"]

            response_data = save_transaction(
                request.POST["transaction_type"], amt, desc, seller, buyer
            )
            if response_data["success"]:
                txn = response_data["txn_obj"]
                messages.success(request, f"Success! Payment success. txnId:{txn.id}")
            else:
                messages.error(request, response_data["msg"])
            return redirect("frontendapp:home")

    else:
        form = TransactionForm()
    latest_trans = get_transaction_queryset(request.user)[:5]
    return render(
        request, "home.html", {"transaction_form": form, "transactions": latest_trans}
    )


class ExchangeView(ListView):
    paginate_by = 20
    template_name = "frontendapp/exchanges.html"
    context_object_name = "exchanges"

    def get_queryset(self):
        return Exchange.objects.all()


class UserList(ListView):
    paginate_by = 20
    template_name = "frontendapp/user_list.html"
    context_object_name = "users"

    def get_queryset(self):
        query = self.request.GET.get("q", "")
        queryset = User.objects.filter(exchange__code=self.kwargs["exchange"]).order_by(
            "first_name"
        )
        if query:
            queryset = queryset.filter(
                Q(username__icontains=query) | Q(first_name__icontains=query)
            )
        return queryset


class UserDetail(FormView):
    template_name = "frontendapp/user_detail.html"
    form_class = ListingForm

    def get_context_data(self, **kwargs):
        user = User.objects.get(id=self.kwargs["user"])
        ctx = super().get_context_data(**kwargs)
        extra = {
            "current_user": user,
            "transactions": get_transaction_queryset(user),
            "userlistings": Listing.objects.filter(user=user),
        }
        return ctx | extra

    @method_decorator(login_required)
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

    def form_valid(self, form):
        # This method is called when valid form data has been POSTed.
        # It should return an HttpResponse.
        obj = form.save(commit=False)
        obj.listing_type = self.request.POST["listing_type"]
        obj.user = self.request.user
        obj.save()
        messages.success(self.request, f"Listing activated: {obj}.")
        return redirect(
            "frontendapp:user_detail",
            exchange=self.kwargs["exchange"],
            user=self.kwargs["user"],
        )


@method_decorator([login_required], name="dispatch")
class ListingDeleteView(DeleteView):
    model = Listing

    def get_queryset(self):
        return Listing.objects.filter(user=self.request.user)

    def get_success_url(self):
        u = self.request.user
        return reverse(
            "frontendapp:user_detail",
            kwargs={"exchange": u.exchange.code, "user": u.id},
        )


class ListingPreviewView(DetailView):
    model = Listing
    template_name = "frontendapp/listing_detail.html"
