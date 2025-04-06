from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
from django import forms
from django.forms.utils import ValidationError
from coinapp.models import Exchange, Listing

User = get_user_model()


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    tandc = forms.BooleanField(label="Terms and Conditions.")

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "exchange",
            "username",
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


class ExchangeForm(forms.ModelForm):
    def clean_code(self):
        if len(self.cleaned_data["code"]) != 4:
            raise ValidationError(
                "Exchange Code must be 4 characters long", code="invalid_code"
            )
        return self.cleaned_data["code"].upper()

    class Meta:
        model = Exchange
        fields = ("code", "name", "address", "country")


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
            "detail": DetailWidget(), # attrs={'rows': 40}),
        }
        error_messages = {
            'detail': {
                'required': "Please click the above button(Generate Detail from Heading) to fill the Detail using AI.",
            },
        }
