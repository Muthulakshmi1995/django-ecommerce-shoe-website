def cart_summary(request):
    cart = request.session.get("cart", {})
    return {"cart_count": sum(int(item.get("quantity", 1)) for item in cart.values())}
