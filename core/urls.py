from django.urls import path
from . import views

app_name = "core"
urlpatterns = [
    path("", views.home, name="home"), # HomeView.as_view()
    path("transaction_confirm/<int:trans_record_id>/", 
         views.transaction_confirm, name="transaction_confirm"),
]