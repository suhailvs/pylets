from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Listing, GeneralSettings, Transaction, User, UserVerification, Exchange

# https://stackoverflow.com/a/60084208/2351696
extrafields = ('image','exchange','phone','government_id','date_of_birth','balance')
class CustomUserAdmin(UserAdmin):
    # see -> env/lib/python3.12/site-packages/django/contrib/auth/admin.py
    fieldsets = UserAdmin.fieldsets + (('Other fields',{'fields':extrafields}),)
    list_display = UserAdmin.list_display +  ('phone','date_of_birth','balance','balance_from_txns')# + extrafields 
    list_filter = ("is_active", "exchange")

admin.site.register(GeneralSettings)
admin.site.register(User, CustomUserAdmin)
admin.site.register(Exchange)
admin.site.register(Listing)
admin.site.register(Transaction)
