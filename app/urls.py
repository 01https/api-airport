from django.urls import path, include
from django.contrib import admin
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airport/", include("airport.urls")),
    path("api/user/", include("user.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
    path("api/doc/", SpectacularAPIView.as_view(), name="schema"),
   path("api/doc/swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
   path("api/doc/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]
