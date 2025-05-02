from django.urls import include, path
from rest_framework.routers import DefaultRouter
from . import views

app_name = 'api'

router = DefaultRouter()
router.register('listings', views.ListingModelViewSet, basename='listing-api')
router.register('users', views.UserReadOnlyViewSet, basename='userreadonly-api')

urlpatterns = [    
    path('', include(router.urls)),
    path('ajax/',views.AjaxView.as_view()),
    path('transactions/',views.Transactions.as_view()),
    path('login/', views.CustomAuthToken.as_view()),
    path('registration/', views.CreateUserView.as_view()),
    path('verifyuser/', views.VerifyUserView.as_view()),
]
