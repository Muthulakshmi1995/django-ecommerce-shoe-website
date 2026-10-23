import json
from decimal import Decimal
import traceback
from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.core.management import call_command
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST
from .models import Category, Product, Order, OrderItem, Enquiry

def _cart_items(request):
    cart = request.session.get("cart", {})
    items, total = [], Decimal("0.00")
    for key, row in cart.items():
        try:
            product = Product.objects.get(pk=int(key), active=True)
            qty = max(1, min(int(row.get("quantity", 1)), 20))
            price = product.price
            subtotal = price * qty
            items.append({"product": product, "quantity": qty, "size": row.get("size", "41"),
                          "colour": row.get("colour", "Black"), "subtotal": subtotal})
            total += subtotal
        except (Product.DoesNotExist, ValueError, TypeError):
            continue
    return items, total

def _ensure_demo_catalog():
    """Populate the sample catalogue on first visit after migrations.

    This prevents an empty home page when a student forgets to run the seed command.
    The management command uses update_or_create, so repeated calls are safe.
    """
    if not Product.objects.exists() or not Category.objects.exists():
        call_command("seed_products", verbosity=0)


def home(request):
    _ensure_demo_catalog()
    categories = Category.objects.all()
    featured = Product.objects.filter(active=True, featured=True).select_related("category")[:8]
    trending = Product.objects.filter(active=True).select_related("category")[:8]
    return render(request, "store/home.html", {"categories": categories, "featured": featured, "trending": trending})

def shop(request):
    _ensure_demo_catalog()
    products = Product.objects.filter(active=True).select_related("category")
    cat = request.GET.get("category")
    search = request.GET.get("q", "").strip()
    sort = request.GET.get("sort", "")
    if cat:
        products = products.filter(category__slug=cat)
    if search:
        products = products.filter(name__icontains=search) | products.filter(brand__icontains=search)
    if sort == "price_low":
        products = products.order_by("price")
    elif sort == "price_high":
        products = products.order_by("-price")
    elif sort == "rating":
        products = products.order_by("-rating")
    return render(request, "store/shop.html", {"products": products, "categories": Category.objects.all(),
                                                "selected_category": cat, "search": search, "sort": sort})

def category(request, slug):
    _ensure_demo_catalog()
    # Accept common URL variations (men/mens, woman/women, kid/kids).
    aliases = {"mens": "men", "man": "men", "male": "men",
               "womens": "women", "woman": "women", "female": "women",
               "kid": "kids", "child": "kids", "children": "kids"}
    slug = aliases.get(slug.lower(), slug.lower())
    cat = get_object_or_404(Category, slug=slug)
    products = Product.objects.filter(active=True, category=cat).select_related("category")
    return render(request, "store/shop.html", {"products": products, "categories": Category.objects.all(),
                                                "selected_category": slug, "page_title": cat.name, "search": ""})

def product_detail(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    related = Product.objects.filter(active=True, category=product.category).exclude(pk=pk)[:4]
    return render(request, "store/product_detail.html", {"product": product, "related": related})

@require_POST
def add_to_cart(request, pk):
    product = get_object_or_404(Product, pk=pk, active=True)
    try:
        qty = max(1, min(int(request.POST.get("quantity", "1") or 1), 20))
    except (TypeError, ValueError):
        messages.error(request, "Please select a valid quantity.")
        return redirect(request.META.get("HTTP_REFERER") or "store:cart")
    size = request.POST.get("size", product.size_list[0] if product.size_list else "41")
    colour = request.POST.get("colour", product.colour_list[0] if product.colour_list else "Black")
    cart = request.session.get("cart", {})
    key = str(product.pk)
    if key in cart:
        cart[key]["quantity"] = min(20, int(cart[key].get("quantity", 1)) + qty)
        cart[key]["size"], cart[key]["colour"] = size, colour
    else:
        cart[key] = {"quantity": qty, "size": size, "colour": colour}
    request.session["cart"] = cart
    request.session.modified = True
    messages.success(request, f"{product.name} added to your cart.")
    if request.POST.get("next") == "checkout":
        return redirect("store:checkout")
    return redirect(request.META.get("HTTP_REFERER") or "store:cart")

@require_POST
def update_cart(request, pk):
    cart = request.session.get("cart", {})
    key = str(pk)
    if key in cart:
        try:
            qty = int(request.POST.get("quantity", "1"))
            if qty < 1:
                cart.pop(key, None)
            else:
                cart[key]["quantity"] = min(qty, 20)
                cart[key]["size"] = request.POST.get("size", cart[key].get("size", "41"))
                cart[key]["colour"] = request.POST.get("colour", cart[key].get("colour", "Black"))
        except ValueError:
            messages.error(request, "Please select a valid quantity.")
        request.session["cart"] = cart
        request.session.modified = True
    return redirect("store:cart")

@require_POST
def remove_from_cart(request, pk):
    cart = request.session.get("cart", {})
    cart.pop(str(pk), None)
    request.session["cart"] = cart
    request.session.modified = True
    messages.info(request, "Item removed from your cart.")
    return redirect("store:cart")

def cart_view(request):
    items, total = _cart_items(request)
    return render(request, "store/cart.html", {"items": items, "total": total})

def about(request):
    return render(request, "store/about.html")

def contact(request):
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        email = request.POST.get("email", "").strip()
        message = request.POST.get("message", "").strip()
        if name and email and message:
            Enquiry.objects.create(name=name, email=email, phone=request.POST.get("phone", "").strip(),
                                   subject=request.POST.get("subject", "").strip(), message=message)
            messages.success(request, "Thank you! Your enquiry has been submitted.")
            return redirect("store:contact")
        messages.error(request, "Please fill in your name, email and message.")
    return render(request, "store/contact.html")

def checkout(request):
    items, total = _cart_items(request)

    if not items:
        messages.info(request, "Your cart is empty. Add a shoe before checkout.")
        return redirect("store:shop")

    if request.method == "POST":
        fields = {
            k: request.POST.get(k, "").strip()
            for k in [
                "customer_name", "email", "phone",
                "address", "city", "postal_code"
            ]
        }

        if not all(fields.values()):
            messages.error(request, "Please fill in every delivery field.")
            return render(request, "store/checkout.html", {
                "items": items, "total": total, "fields": fields
            })

        order = Order.objects.create(
            customer_name=fields["customer_name"],
            email=fields["email"],
            phone=fields["phone"],
            address=fields["address"],
            city=fields["city"],
            postal_code=fields["postal_code"],
            total=total,
            user=request.user if request.user.is_authenticated else None,
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item["product"],
                product_name=item["product"].name,
                size=item["size"],
                colour=item["colour"],
                quantity=item["quantity"],
                unit_price=item["product"].price,
            )

        try:
            import razorpay

            if not settings.RAZORPAY_KEY_ID or not settings.RAZORPAY_KEY_SECRET:
                raise ValueError("Razorpay test keys are not configured.")

            client = razorpay.Client(
                auth=(
                    settings.RAZORPAY_KEY_ID,
                    settings.RAZORPAY_KEY_SECRET,
                )
            )

            rz_order = client.order.create({
                "amount": int(total * 100),
                "currency": "INR",
                "receipt": f"stepup-{order.pk}",
                "notes": {"stepup_order_id": str(order.pk)},
            })

            order.razorpay_order_id = rz_order["id"]
            order.save(update_fields=["razorpay_order_id"])

            request.session["pending_order_id"] = order.pk

            return render(request, "store/payment.html", {
                "order": order,
                "razorpay_order_id": rz_order["id"],
                "razorpay_key_id": settings.RAZORPAY_KEY_ID,
                "amount_paise": int(total * 100),
                "customer_name": fields["customer_name"],
                "email": fields["email"],
                "phone": fields["phone"],
            })

        except Exception as exc:
            import traceback
            traceback.print_exc()

            order.status = "failed"
            order.save(update_fields=["status"])

            messages.error(
                request,
                f"Razorpay order error: {type(exc).__name__}: {exc}"
            )
            return redirect("store:checkout")

    return render(request, "store/checkout.html", {
        "items": items,
        "total": total,
        "fields": {},
    })

@require_POST
def verify_payment(request):
    order_id = request.session.get("pending_order_id")
    if not order_id:
        messages.error(request, "No pending payment was found.")
        return redirect("store:cart")
    order = get_object_or_404(Order, pk=order_id)
    payment_id = request.POST.get("razorpay_payment_id", "")
    rz_order_id = request.POST.get("razorpay_order_id", "")
    signature = request.POST.get("razorpay_signature", "")
    if not (settings.RAZORPAY_KEY_ID and settings.RAZORPAY_KEY_SECRET and payment_id and rz_order_id and signature):
        messages.error(request, "Payment details were incomplete.")
        return redirect("store:checkout")
    try:
        import razorpay
        client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET))
        client.utility.verify_payment_signature({
            "razorpay_order_id": rz_order_id, "razorpay_payment_id": payment_id,
            "razorpay_signature": signature,
        })
        order.status = "paid"
        order.razorpay_payment_id = payment_id
        order.save(update_fields=["status", "razorpay_payment_id"])
        request.session["cart"] = {}
        request.session.pop("pending_order_id", None)
        request.session.modified = True
        return redirect("store:order_success", order_id=order.pk)
    except Exception as exc:
        print("RAZORPAY ERROR:", repr(exc),flush=True)
        order.status = "failed"
        order.save(update_fields=["status"])
        messages.error(request, "Payment verification failed. Please contact the store before retrying.")
        return redirect("store:checkout")

def order_success(request, order_id):
    order = get_object_or_404(Order, pk=order_id)
    return render(request, "store/order_success.html", {"order": order})


def customer_login(request):
    if request.user.is_authenticated:
        return redirect("store:home")
    error = ""
    if request.method == "POST":
        username = request.POST.get("username", "").strip()
        password = request.POST.get("password", "")
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f"Welcome back, {user.username}!")
            redirect_to = request.POST.get("next") or request.GET.get("next") or reverse("store:home")
            if not url_has_allowed_host_and_scheme(redirect_to, allowed_hosts={request.get_host()}):
                redirect_to = reverse("store:home")
            return redirect(redirect_to)
        error = "Username or password is incorrect."
    return render(request, "store/login.html", {"error": error})

def customer_register(request):
    if request.user.is_authenticated:
        return redirect("store:home")
    form = UserCreationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, "Your StepUp account has been created.")
        return redirect("store:home")
    return render(request, "store/register.html", {"form": form})

def customer_logout(request):
    logout(request)
    messages.info(request, "You have been logged out.")
    return redirect("store:home")
