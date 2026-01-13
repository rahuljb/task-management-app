from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.shortcuts import redirect
def home(request):
    return redirect("panel_login")
urlpatterns = [
    # JWT
    path("api/token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("api/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("panel/", include("adminpanel.urls")),
    path("", home),

    # Tasks API
    path("api/", include("tasks.urls")),
    

]   