from django.contrib.auth import get_user_model
from django.test import TestCase, Client
from django.urls import reverse
from .models import Category, Product

class StoreFlowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Men", slug="men")
        self.product = Product.objects.create(
            category=self.category, name="Test shoe", brand="StepUp",
            price="1999.00", mrp="2499.00", image="store/products/asset_04.png",
            sizes="41,42,43", colours="Black,Tan", stock=10, featured=True,
        )
        self.client = Client()

    def test_home_loads(self):
        response = self.client.get(reverse("store:home"))
        self.assertEqual(response.status_code, 200)

    def test_add_to_cart_and_cart_page(self):
        response = self.client.post(reverse("store:add_to_cart", args=[self.product.pk]), {
            "quantity": "2", "size": "42", "colour": "Tan"
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("store:cart"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test shoe")

    def test_login_rejects_external_redirect(self):
        user = get_user_model().objects.create_user(username="alice", password="securepass123")
        response = self.client.post(
            reverse("store:login") + "?next=https://evil.example",
            {"username": user.username, "password": "securepass123"},
            follow=False,
        )
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("store:home"), fetch_redirect_response=False)

    def test_invalid_cart_quantity_uses_safe_redirect(self):
        response = self.client.post(reverse("store:add_to_cart", args=[self.product.pk]), {"quantity": "invalid"})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse("store:cart"), fetch_redirect_response=False)
