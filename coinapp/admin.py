from django.contrib import admin
from .models import Listing, GeneralSettings, Transaction,Block

# Register your models here.
admin.site.register(Listing)
admin.site.register(GeneralSettings)
admin.site.register(Transaction)
admin.site.register(Block)
