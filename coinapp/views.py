from openai import OpenAI
from django.contrib.auth import get_user_model
from django.views.generic import CreateView, ListView, DeleteView, DetailView
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login
from django.utils.decorators import method_decorator
from django.db.models import Q, F, BooleanField, Case, When
from django.db import transaction
from django.contrib import messages
from django.urls import reverse_lazy, reverse
from django.views.generic.edit import FormView
from django.http import HttpResponse
from django.conf import settings

from coinapp.models import Transaction, Listing, GeneralSettings, Exchange
from coinapp.forms import (
    SignUpForm,
    SignUpFormWithoutExchange,
    TransactionForm,
    ExchangeForm,
    ListingForm,
)

User = get_user_model()


def about_view(request):
    about_count = GeneralSettings.objects.get(key="about")
    about_count.value = int(about_count.value) + 1
    about_count.save()
    return render(request, "about.html")


class SignUpJoinView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("coinapp:home")
    template_name = "registration/signup_join.html"


class SignUpNewView(CreateView):
    form_class = SignUpFormWithoutExchange
    # success_url = reverse_lazy("coinapp:home")
    template_name = "registration/signup_new.html"

    def form_valid(self, form):
        ctx = self.get_context_data()
        exchange_form = ctx["exchange_form"]
        if exchange_form.is_valid() and form.is_valid():
            with transaction.atomic():
                user_obj = form.save()
                exchange_obj = exchange_form.save(commit=False)
                exchange_obj.admin = user_obj
                exchange_obj.save()
                user_obj.exchange=exchange_obj
                user_obj.save()
                login(self.request, user_obj)
                return redirect(reverse_lazy("coinapp:home"))
        else:
            return self.render_to_response(self.get_context_data(form=form))

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        if self.request.POST:
            ctx["exchange_form"] = ExchangeForm(self.request.POST)
        else:
            ctx["exchange_form"] = ExchangeForm()
        return ctx


def get_transactions(user):
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
            if request.POST["transaction_type"] == "buyer":
                # send money
                seller, buyer = buyer, seller
            with transaction.atomic():
                seller.amount = F("amount") + amt
                buyer.amount = F("amount") - amt
                seller.save(update_fields=["amount"])
                buyer.save(update_fields=["amount"])
                txn = Transaction.objects.create(
                    seller=seller,
                    buyer=buyer,
                    description=desc,
                    amount=amt,
                )
                messages.success(request, f"Success! Payment success. txnId:{txn.id}")
            return redirect("coinapp:home")

    else:
        form = TransactionForm()
    latest_trans = get_transactions(request.user)[:5]
    return render(
        request, "home.html", {"transaction_form": form, "transactions": latest_trans}
    )


class ExchangeView(ListView):
    paginate_by = 20
    template_name = "coinapp/exchanges.html"
    context_object_name = "exchanges"

    def get_queryset(self):
        return Exchange.objects.all()


class UserList(ListView):
    paginate_by = 20
    template_name = "coinapp/user_list.html"
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
    template_name = "coinapp/user_detail.html"
    form_class = ListingForm

    def get_context_data(self, **kwargs):
        user = User.objects.get(id=self.kwargs["user"])
        ctx = super().get_context_data(**kwargs)
        extra = {
            "current_user": user,
            "transactions": get_transactions(user),
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
            "coinapp:user_detail",
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
            "coinapp:user_detail", kwargs={"exchange": u.exchange.code, "user": u.id}
        )


class ListingPreviewView(DetailView):
    model = Listing
    # template_name = 'classroom/teachers/question_preview.html'
    # pk_url_kwarg = 'question_pk'

    # def get_context_data(self, **kwargs):
    #     question = self.get_object()
    #     kwargs['quiz'] = question.quiz
    #     return super().get_context_data(**kwargs)

    # def get_queryset(self):
    #     return Question.objects.filter(quiz__owner=self.request.user)


def github_models_api(heading):
    text = f"""Create an offering description for local exchange trading system 
        where I can offer activity or things like {heading}"""
    client = OpenAI(
        base_url="https://models.inference.ai.azure.com",
        api_key=settings.GITHUB_TOKEN,
    )
    system_msg = "You are a helpful assistant."
    response = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system_msg},
            {"role": "user", "content": text},
        ],
        model="gpt-4o",
        temperature=1.0,
        max_tokens=1000,
        top_p=1.0,
    )
    return response.choices[0].message.content


def ajax_views(request, purpose):
    resp = ""
    if purpose == "get_balance":
        # i think it is not used
        resp = User.objects.get(username=request.GET.get("username")).amount
    elif purpose == "ai":
        # ajax/ai/?details=
        resp = github_models_api(request.GET.get("details"))
    return HttpResponse(resp)


"""
@login_required
def ajax_views(request, purpose):
    resp = ''
    if purpose == "get_balance":
        # i think it is not used
        resp = User.objects.get(username=request.GET.get("username")).amount
    elif purpose == "delete_listing":
        obj = Listing.objects.get(id=request.GET.get("listing"))
        if obj.user == request.user:
            obj.delete()
            resp = 'listing_deleted'
    return HttpResponse(resp)


class UserDetail(View):
    def get(self, request, **kwargs):
        user = User.objects.get(id=kwargs["user"])
        return render(
            request,
            "coinapp/user_detail.html",
            {
                "current_user": user,
                "categories": misc.CATEGORIES,
                "transactions": get_transactions(user),
                "userlistings": Listing.objects.filter(user=user),
            },
        )

    @method_decorator(login_required)
    def post(self, request, **kwargs):
        if request.user.pk == kwargs["user"]:
            user_action = request.POST["action"]
            if user_action == "add":
                listing = Listing.objects.create(
                    user=request.user,
                    category=request.POST["category"],
                    heading=request.POST["heading"],
                    detail=request.POST["detail"],
                    rate=(
                        request.POST["rate"]
                        if request.POST["listing_type"] == "O"
                        else ""
                    ),
                    listing_type=request.POST["listing_type"],
                )
                messages.success(request, f"Listing activated: {listing}.")
            elif user_action == "remove":
                print("Need to remove offering")
                # if my_offerings.count() < 2:
                #     messages.warning(request, "Error: 1 offering is required..")
                # else:
                #     my_offerings.remove(offering)
                #     messages.info(request, f"Listing deactivated: {offering}.")
            else:
                messages.warning(request, "Error: Invalid Action..")
        else:
            messages.warning(request, "Error: You can only create your listing..")
        return redirect(
            "coinapp:user_detail", exchange=kwargs["exchange"], user=kwargs["user"]
        )

        @method_decorator(login_required, name="dispatch")
class HomeView(View):
    def get(self, request):
        return render(
            request,
            "home.html",
            {
                "transaction_form": TransactionForm(),
                "transactions": get_transactions(request.user)[:5],
                "users": User.objects.exclude(username=request.user.username),
                "total": User.objects.aggregate(total=Sum("amount")),
            },
        )

    def post(self, request):
        form = TransactionForm(request.POST)

        
        buyer = User.objects.get(username=request.POST["to_user"])
        seller = request.user
        amt = request.POST["amount"]
        if buyer == seller:
            messages.warning(request, "Error! Seller and buyer are same.")
        elif amt.isnumeric():
            description = request.POST["description"]
            with transaction.atomic():
                seller.amount = F("amount") + amt
                buyer.amount = F("amount") - amt
                seller.save()
                buyer.save()
                txn = Transaction.objects.create(
                    seller=seller, buyer=buyer, description=description, amount=amt
                )
                messages.success(request, f"Success! Payment success. txnId:{txn.id}")

        else:
            messages.warning(request, "Error! Amount must be a number.")
        return redirect("coinapp:home")
"""
