from django.urls import path
from .views import order_delete, view_orders, order_edit, order_add, download_excel


urlpatterns = [
    path("list/", view_orders, name="view_orders"),
    path("add/", order_add, name="add_order"),
    path("edit/<int:pk>/", order_edit, name="edit_order"),
    path("delete/<int:pk>/", order_delete, name="delete_order"),
    path("download/", download_excel, name="download_excel"),
]
