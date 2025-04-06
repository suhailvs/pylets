from django.contrib import admin
from django.urls import path, include
from frontendapp.views import SignUpJoinView, SignUpNewView
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

urlpatterns = [
    path("", include("frontendapp.urls")),
    path("api/v1/", include("api.urls")),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path("admin/", admin.site.urls),
    # path("about/", about_view, name='about'), #TemplateView.as_view(template_name="about.html"), name='about'),
    path("accounts/", include("django.contrib.auth.urls")),
    path("accounts/signup_join/", SignUpJoinView.as_view(), name="signup_join"),
    path("accounts/signup_new/", SignUpNewView.as_view(), name="signup_new"),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
