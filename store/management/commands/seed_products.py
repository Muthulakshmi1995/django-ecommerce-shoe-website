from django.core.management.base import BaseCommand
from store.models import Category, Product

class Command(BaseCommand):
    help = "Create the StepUp sample categories and shoe products."

    def handle(self, *args, **options):
        categories = {
            "Men": ("men", "store/products/asset_09.png", "Everyday trainers, boots and smart shoes."),
            "Women": ("women", "store/products/asset_02.png", "Flats, heels, sandals and everyday favourites."),
            "Kids": ("kids", "store/products/asset_21.png", "Comfortable, colourful shoes for little feet."),
        }
        objects = {}
        for name, (slug, image, desc) in categories.items():
            cat, _ = Category.objects.update_or_create(slug=slug, defaults={"name": name, "image": image, "description": desc})
            objects[name] = cat
        products = [
            ("Osaga Neptune Mens Lace Up Trainer", "Osaga", "Men", "store/products/asset_04.png", "2799", "3299", "4.8", "8", "Black,Navy,White"),
            ("Mateo Leather Lace-up Sneakers", "Mateo", "Men", "store/products/asset_44.png", "3999", "4499", "4.6", "7", "Black,Brown,White"),
            ("Urban Territory Beaumont Mens Black Warm Boots", "Urban Territory", "Men", "store/products/asset_14.png", "2799", "3299", "4.5", "5", "Black,Brown"),
            ("Urban Territory Bill Mens Brown Lace Up Boot", "Urban Territory", "Men", "store/products/asset_45.png", "2999", "3499", "4.4", "5", "Brown,Black"),
            ("Comfy Steps Harlan Mens Tan Boat Shoe", "Comfy Steps", "Men", "store/products/asset_20.png", "2799", "3299", "5.0", "16", "Tan,Black,Red"),
            ("XL Weaver Mens Lace Up Trainer", "XL", "Men", "store/products/asset_34.png", "1799", "2299", "4.7", "10", "Black,Red,White"),
            ("Double Strap Sandals", "StepUp", "Men", "store/products/asset_26.png", "2999", "3499", "4.5", "6", "Brown,Black,White"),
            ("Comfy Steps Lustral White Leather Slippers", "Comfy Steps", "Men", "store/products/asset_47.png", "1995", "2499", "4.8", "9", "White,Brown"),
            ("Daisy Print Girls Sandal", "Calista", "Kids", "store/products/asset_30.jpg", "2899", "3299", "4.6", "5", "Pink,White"),
            ("Colby Boys Blue Dinosaur Canvas", "Colby", "Kids", "store/products/asset_28.jpg", "3299", "3699", "4.8", "4", "Blue,White"),
            ("Girls Pink Winter Boots", "StepUp Kids", "Kids", "store/products/asset_17.png", "1599", "1999", "4.5", "3", "Pink,White"),
            ("Kids Colourful Slip-on", "StepUp Kids", "Kids", "store/products/asset_31.png", "1299", "1599", "4.4", "4", "Purple,Pink"),
            ("Women's Pearl Strap Sandal", "StepUp", "Women", "store/products/asset_23.png", "2499", "2999", "4.7", "8", "Tan,White,Black"),
            ("Women's White Comfort Trainer", "StepUp", "Women", "store/products/asset_32.png", "2199", "2699", "4.6", "5", "White,Black"),
            ("Women's Navy Comfort Sandal", "StepUp", "Women", "store/products/asset_29.png", "1999", "2499", "4.5", "6", "Navy,Tan"),
            ("Women's Floral Blue Slipper", "StepUp", "Women", "store/products/asset_33.png", "1499", "1899", "4.4", "4", "Blue,White"),
            ("Red Party High Heels", "StepUp", "Women", "store/products/asset_10.jpg", "3499", "3999", "4.8", "12", "Red,Black"),
            ("Brown Leather Loafer", "StepUp", "Men", "store/products/asset_24.png", "2799", "3299", "4.6", "7", "Brown,Black"),
        ]
        for i, (name, brand, category, image, price, mrp, rating, reviews, colours) in enumerate(products):
            img2 = image
            img3 = image
            img4 = image
            if "Boat Shoe" in name:
                img2, img3, img4 = "store/products/asset_36.png", "store/products/asset_55.png", "store/products/asset_03.png"
            Product.objects.update_or_create(name=name, defaults={
                "category": objects[category], "brand": brand,
                "description": f"{name}. Designed for comfort, everyday wear and dependable style. Choose your size and colour before adding to your cart.",
                "price": price, "mrp": mrp, "image": image, "image_2": img2, "image_3": img3, "image_4": img4,
                "colours": colours, "sizes": "41,42,43,44,45", "rating": rating, "reviews": reviews,
                "stock": 25, "featured": i < 8, "active": True,
            })
        self.stdout.write(self.style.SUCCESS(f"StepUp demo data ready: {Category.objects.count()} categories, {Product.objects.count()} products."))
