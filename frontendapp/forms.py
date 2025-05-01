import pycountry

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms.utils import ValidationError
from coinapp.models import Exchange, Listing
from api.serializers import generate_username
User = get_user_model()


class SignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    email = forms.EmailField(required=True)
    tandc = forms.BooleanField(label="Terms and Conditions.")

    def clean_government_id(self):
        govt_id = self.cleaned_data["government_id"]
        if govt_id:
            if User.objects.filter(government_id=govt_id).exists():
                raise ValidationError({'government_id': 'This Government ID must be unique.'})
        return govt_id
    
    def save(self, commit=True, exchange_obj=None):
        user = super().save(commit=commit)
        if exchange_obj:
            # new exchange
            user.username = generate_username(exchange_obj.code)
            user.exchange = exchange_obj
        else:
            user.username = generate_username(user.exchange.code) 
        user.save()
        return user

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "exchange",
            "phone",
            "first_name",
            "email",
            "government_id",
            "date_of_birth",
            "password1",
            "password2",
            "tandc",
        )


class SignUpFormWithoutExchange(SignUpForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop("exchange")


def get_country_choices():
    countries = [(c.alpha_2, c.name) for c in pycountry.countries]
    return [('','--select--')]+sorted(countries, key=lambda x: x[1])


def get_state_choices(country_code):
    cities = list(pycountry.subdivisions.get(country_code=country_code))
    return [(city.code, city.name) for city in cities]


class ExchangeForm(forms.ModelForm):
    country_city = forms.ChoiceField(choices=[], label="City")

    def clean_code(self):
        if len(self.cleaned_data["code"]) != 4:
            raise ValidationError(
                "Exchange code must be exactly 4 characters long.", code="invalid_code"
            )
        return self.cleaned_data["code"].upper()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        dummy_country_code = self.data.get("dummy_country_dropdown")
        self.fields["dummy_country_dropdown"] = forms.ChoiceField(
            choices=get_country_choices(), label="Country"
        )
        # need to set city while form reload
        if dummy_country_code:
            self.fields["country_city"].choices = get_state_choices(dummy_country_code)
        self.order_fields(
            ["name", "code", "address", "dummy_country_dropdown", "country_city"]
        )

    class Meta:
        model = Exchange
        fields = ("code", "name", "address", "postal_code","country_city")


class TransactionForm(forms.Form):
    CHOICES = [
        ("seller", "Enter as seller(Receive money)"),
        ("buyer", "Enter as buyer(Send money)"),
    ]
    transaction_type = forms.ChoiceField(
        initial="seller",
        widget=forms.RadioSelect,
        choices=CHOICES,
    )
    to_user = forms.ModelChoiceField(queryset=User.objects.all())
    description = forms.CharField()
    amount = forms.IntegerField()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["to_user"].label_from_instance = (
            lambda u: f"{u.username}|{u.first_name}|amt:{u.balance}rs"
        )


class DetailWidget(forms.Textarea):
    template_name = "frontendapp/parts/_detail_widget.html"


class ListingForm(forms.ModelForm):
    class Meta:
        model = Listing
        fields = ("category", "title", "description", "rate", "image")
        widgets = {
            "detail": DetailWidget(),  # attrs={'rows': 40}),
        }
        error_messages = {
            "detail": {
                "required": "Please click the above button(Generate Detail from Heading) to fill the Detail using AI.",
            },
        }
