import math
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.models import Q, Sum, Count
from django.core.paginator import Paginator
from django.utils import timezone
from django.http.response import HttpResponse, JsonResponse
from django.contrib.auth import get_user_model
from core.constants import BILL_PER_BOOK, ITEM_NAMES

from export.excel import export_data

from .models import Order
from .forms import OrderForm
import logging

logger = logging.getLogger(__name__)

User = get_user_model()


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
            # print(form.data)
            if form.is_valid():
                # print("Form Valid")
                form.save()
                return redirect("view_orders")
        return render(request, "order/edit.html", {"form": form, "order": order})
    except Exception as e:
        messages.error(request, e.args[0])
        return render(request, "order/edit.html", {"form": form, "order": order})


@login_required
def view_orders(request):
    search = request.GET.get("search", None)

    total_summary = (
        (
            Order.objects.prefetch_related("dealer")
            .filter(dealer=request.user)
            .aggregate(
                user_total=Sum("total_amount"),
                total_orders=Count("pk"),
            )
        )
        if request.user.is_superuser == False
        else (
            Order.objects.prefetch_related("dealer").aggregate(
                user_total=Sum("total_amount"),
                total_orders=Count("pk"),
            )
        )
    )
    total_summary["user_total"] = total_summary["user_total"] or 0
    total_summary["total_orders"] = total_summary["total_orders"] or 0
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
    return render(
        request,
        "order/list_orders.html",
        {"page": page, "total_summary": total_summary},
    )


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


@login_required
def dealer_total_detail(request):
    try:
        qs = (
            Order.objects.prefetch_related("dealer")
            .all()
            .values_list("dealer", "bill_number", "total_amount", "amount_paid")
        )
        books = []
        issued_books = User.objects.all().values_list("books", flat=True)
        for i in issued_books:
            for a in i:
                books.append(a)
        books.sort()

        if request.user.is_superuser:
            data = []
            for book in books:
                filtered_qs = list(
                    filter(lambda x: math.ceil(x[1] / BILL_PER_BOOK) == book, qs)
                )
                data.append(
                    {
                        "book": book,
                        "total": sum([i[2] for i in filtered_qs]) or 0,
                        "paid": sum([i[3] for i in filtered_qs]) or 0,
                        "total_orders": len(filtered_qs),
                    }
                )
        else:
            data = []
            for book in request.user.books:
                filtered_qs = list(
                    filter(lambda x: math.ceil(x[1] / BILL_PER_BOOK) == book, qs)
                )
                data.append(
                    {
                        "book": book,
                        "total": sum([i[2] for i in filtered_qs]) or 0,
                        "paid": sum([i[3] for i in filtered_qs]) or 0,
                        "total_orders": len(filtered_qs),
                    }
                )
        return render(request, "order/total_summary.html", {"data": data})
    except Exception as e:
        logger.exception(e)
        return JsonResponse({"detail": "error occurred"})
    

@login_required
def dispatch_view(request):
    try:
        book = request.GET.get("book", None)
        bill_number = request.GET.get("bill_number", None)
        if book:
            book = int(book)
            order = Order.objects.prefetch_related("dealer").filter(
                bill_number__gt=(book-1) * BILL_PER_BOOK,
                bill_number__lte=book * BILL_PER_BOOK,
            )
            book_total_data = {}
            for item in ITEM_NAMES[1]:
                book_total_data[item] = sum([getattr(i, item) for i in order])

            return render(
                request,
                "order/dispatch.html",
                {
                    "book_orders": order,
                    "book_total_data": book_total_data,
                    "book": {"number": book, "dealer_name": order[0].dealer.name if order else None},
                },
            )
        elif bill_number:
            bill_number = int(bill_number)
            order = Order.objects.prefetch_related("dealer").filter(
                bill_number=bill_number
            )
            return render(
                request,
                "order/dispatch.html",
                {
                    "book_orders": order,
                    "book": {"number": bill_number // BILL_PER_BOOK + 1, "dealer_name": order[0].dealer.name if order else None},
                },
            )
        else:
            return render(request, "order/dispatch.html")
    except Exception as e:
        messages.error(request, e.args[0])
        return render(request, "order/dispatch.html")
