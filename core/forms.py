
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import UserCreationForm
from django import forms
User = get_user_model()

class SignUpForm(UserCreationForm):
    first_name = forms.CharField(required=True)
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("first_name","username","password1","password2",)

class TransactionForm(forms.Form):
    CHOICES = [
        (True, "Receive money"), # Enter as seller
        (False, "Send money"), # Enter as buyer
    ]
    transaction_type = forms.ChoiceField(
        initial=True,
        widget=forms.RadioSelect,
        choices=CHOICES,
    )
    to_user = forms.ModelChoiceField(queryset=User.objects.all())
    description = forms.CharField()
    amount = forms.IntegerField()