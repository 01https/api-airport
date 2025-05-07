from django.urls import path, include
from django.contrib import admin

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/airport/", include("airport.urls")),
    path("api/user/", include("user.urls")),
    path("__debug__/", include("debug_toolbar.urls"))
]
