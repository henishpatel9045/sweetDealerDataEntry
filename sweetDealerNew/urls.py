from django.contrib import admin
from django.urls import path, include
from django.contrib.auth.views import LoginView, LogoutView


class CustomLoginView(LoginView):
    template_name = "order/login.html"

    def get_success_url(self):
        return "/order/list/"


class CustomLogOutView(LogoutView):
    def get_success_url(self):
        return "/login/"


urlpatterns = [
    path("login/", CustomLoginView.as_view(), name="order_login"),
    path("logout/", CustomLogOutView.as_view(), name="order_logout"),
    path("admin/", admin.site.urls),
    path("order/", include("core.urls")),
    path("__debug__/", include("debug_toolbar.urls")),
]
