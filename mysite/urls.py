from django.contrib import admin
from django.urls import path, include
from coinapp.views import SignUpJoinView, SignUpNewView


from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.views.decorators.csrf import csrf_exempt

# from django.conf import settings
# from django.conf.urls.static import static
urlpatterns = [
    path("", include("coinapp.urls")),
    path("api/v1/", include("api.urls")),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path("admin/", admin.site.urls),
    path('dj-rest-auth/', include('dj_rest_auth.urls')),
    # path("about/", about_view, name='about'), #TemplateView.as_view(template_name="about.html"), name='about'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup_join/", SignUpJoinView.as_view(), name="signup_join"),
    path("accounts/signup_new/", SignUpNewView.as_view(), name="signup_new"),
]
# + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

