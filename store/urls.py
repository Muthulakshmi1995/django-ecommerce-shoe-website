from django.urls import path
from . import views

app_name = "store"
urlpatterns = [
    path("", views.home, name="home"),
    path("shop/", views.shop, name="shop"),
 
    path("category/<slug:slug>/", views.category, name="category"),
    path("product/<int:pk>/", views.product_detail, name="product_detail"),
    path("about/", views.about, name="about"),
    path("login/", views.customer_login, name="login"),
    path("register/", views.customer_register, name="register"),
    path("logout/", views.customer_logout, name="logout"),
    path("contact/", views.contact, name="contact"),
    path("cart/", views.cart_view, name="cart"),
    path("cart/add/<int:pk>/", views.add_to_cart, name="add_to_cart"),
    path("cart/update/<int:pk>/", views.update_cart, name="update_cart"),
    path("cart/remove/<int:pk>/", views.remove_from_cart, name="remove_from_cart"),
    path("checkout/", views.checkout, name="checkout"),
    path("payment/verify/", views.verify_payment, name="verify_payment"),
    path("order/success/<int:order_id>/", views.order_success, name="order_success"),
    path("track-order/", views.track_order, name="track_order"),
    path("my-account/", views.my_account, name="my_account"),
path("my-orders/", views.my_orders, name="my_orders"),
        path("<slug:slug>/", views.category, name="category_short"),
]
