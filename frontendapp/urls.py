from django.urls import path
from . import views

app_name = "frontendapp"
urlpatterns = [
    path("", views.transaction_view, name="home"), # HomeView.as_view()
    path("users/", views.ExchangeView.as_view(), name="exchange_list"),
    path("users/<str:exchange>/", views.UserList.as_view(), name="user_list"),
    path(
        "users/<str:exchange>/<int:user>/",
        views.UserDetail.as_view(),
        name="user_detail",
    ),
    path("stellar_txn/", views.stellar_txn, name="stellar_txn"),    
    path('listing/<int:pk>/delete/', views.ListingDeleteView.as_view(), name='listing_delete'),
    path('listing/<int:pk>/preview/', views.ListingPreviewView.as_view(), name='listing_preview'),
    path("ajax/<str:purpose>/", views.ajax_views, name="ajax_views"), # see https://github.com/gamifications/shihas_bill
]
