from django.urls import path, include


urlpatterns = [
    path("api/airport/", include("airport.urls")),
    path("api/user/", include("user.urls"))
]

app_name = "airport"
