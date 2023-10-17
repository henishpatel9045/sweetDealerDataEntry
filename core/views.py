from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.utils import timezone
from django.http.response import HttpResponse, JsonResponse

from export.excel import export_data

from .models import Order
from .forms import OrderForm
import logging

logger = logging.getLogger(__name__)


class OrderCreateView(CreateView):
    model = Order
    login_required = True
    form_class = OrderForm  # Use the form for order input
    template_name = "order/add.html"
    success_url = reverse_lazy("view_orders")


@login_required
def order_add(request):
    try:
        form = OrderForm()
        if request.method == "POST":
            form = OrderForm(request.POST)
            if form.is_valid():
                form.save()
                return redirect("view_orders")
        return render(request, "order/add.html", {"form": form})
    except Exception as e:
        messages.error(request, e.args[0])
        return render(
            request,
            "order/add.html",
            {
                "form": form,
            },
        )


@login_required
def order_delete(request, pk):
    try:
        order = Order.objects.prefetch_related("dealer").get(bill_number=pk)
        order.delete()
        return redirect("view_orders")
    except Exception as e:
        logger.exception(e)
        messages.error(request, e.args[0])
        return redirect("view_orders")


@login_required
def order_edit(request, pk):
    try:
        order = Order.objects.prefetch_related("dealer").get(bill_number=pk)
        form = OrderForm(instance=order)
        if request.method == "POST":
            form = OrderForm(request.POST, instance=order)
            print(form.data)
            if form.is_valid():
                print("Form Valid")
                form.save()
                return redirect("view_orders")
        return render(request, "order/edit.html", {"form": form, "order": order})
    except Exception as e:
        messages.error(request, e.args[0])
        return render(request, "order/edit.html", {"form": form, "order": order})


@login_required
def view_orders(request):
    search = request.GET.get("search", None)

    if search:
        search = search.strip()
        dealer_orders = (
            Order.objects.prefetch_related("dealer")
            .filter(dealer=request.user)
            .filter(
                Q(bill_number__icontains=search)
                | Q(dealer__username__icontains=search)
                | Q(customer_name__icontains=search)
            )
            if request.user.is_superuser == False
            else Order.objects.prefetch_related("dealer").filter(
                Q(bill_number__icontains=search)
                | Q(dealer__username__icontains=search)
                | Q(customer_name__icontains=search)
            )
        )
    else:
        dealer_orders = (
            Order.objects.prefetch_related("dealer").filter(dealer=request.user)
            if request.user.is_superuser == False
            else Order.objects.prefetch_related("dealer").all()
        )
    paginator = Paginator(dealer_orders, 50)  # Create a Paginator object
    page_number = request.GET.get("page")
    page = paginator.get_page(page_number)
    # Render the template with dealer_orders
    return render(request, "order/list_orders.html", {"page": page})


@login_required
def download_excel(request):
    if request.user.is_superuser == False:
        return JsonResponse({"detail": "You are not authorized to perform this action"})
    try:
        # Generate your Excel data and save it to a BytesIO object
        FILE_NAME = f"Sales Report ({timezone.now().strftime('%d-%m-%Y')}).xlsx"
        excel_buffer = export_data()
        # Create an HTTP response with the Excel data
        response = HttpResponse(content_type="application/ms-excel")
        response["Content-Disposition"] = f'attachment; filename="{FILE_NAME}"'
        response.write(excel_buffer)
        return response
    except Exception as e:
        logger.exception(e)
        return JsonResponse({"detail": "error occurred"})
