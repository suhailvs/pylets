from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register('listings', views.ListingModelViewSet, basename='listing-api')
# router.register('transactions', views.TransactionModelViewSet, basename='transaction-api')

urlpatterns = [    
    path('', include(router.urls)),
    path('user/balance/',views.GetUserBalance.as_view()),
    path('users/',views.GetUsers.as_view()),
    path('user/<int:id>/', views.UserProfileView.as_view(), name='user-profile'),
    path('transactions/',views.Transactions.as_view()),
    path('login/', views.CustomAuthToken.as_view()),
    path('registration/', views.CreateUserView.as_view()),
    path('verifyuser/', views.VerifyUserView.as_view(), name='verify-user'),
]
