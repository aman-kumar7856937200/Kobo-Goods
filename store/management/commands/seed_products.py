
from decimal import Decimal
from urllib.request import Request, urlopen
from urllib.error import URLError, HTTPError

from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.db import transaction

from store.models import Product


PRODUCTS = [
    {
        "name": "Smartphone",
        "brand": "Samsung",
        "category": "Mobiles",
        "description": "A stylish smartphone with a vibrant display, reliable performance and long-lasting battery.",
        "price": "18999",
        "original_price": "22999",
        "stock": 15,
        "rating": 0,
        "review_count": 0,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1511707171634-5f897ff02aa9",
    },
    {
        "name": "Samsung Galaxy Style",
        "brand": "Samsung",
        "category": "Mobiles",
        "description": "A modern Android smartphone designed for smooth everyday performance and entertainment.",
        "price": "24999",
        "original_price": "28999",
        "stock": 20,
        "rating": 4.5,
        "review_count": 28,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1592899677977-9c10ca588bbd",
    },
    {
        "name": "iPhone Pro Edition",
        "brand": "Apple",
        "category": "Mobiles",
        "description": "A premium smartphone experience with an advanced camera and powerful performance.",
        "price": "79999",
        "original_price": "89999",
        "stock": 8,
        "rating": 4.8,
        "review_count": 42,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1591337676887-a217a6970a8a",
    },
    {
        "name": "Redmi Note Series",
        "brand": "Xiaomi",
        "category": "Mobiles",
        "description": "An affordable smartphone with an immersive screen and dependable battery life.",
        "price": "14999",
        "original_price": "17999",
        "stock": 25,
        "rating": 4.3,
        "review_count": 19,
        "badge": "POPULAR",
        "is_featured": True,
        "image": "photo-1512499617640-c74ae3a79d37",
    },
    {
        "name": "OnePlus Performance 5G",
        "brand": "OnePlus",
        "category": "Mobiles",
        "description": "A performance-focused 5G smartphone with a smooth display and fast charging.",
        "price": "32999",
        "original_price": "36999",
        "stock": 12,
        "rating": 4.6,
        "review_count": 31,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1605236453806-6ff36851218e",
    },
    {
        "name": "Premium Laptop",
        "brand": "HP",
        "category": "Laptops",
        "description": "A versatile laptop for productivity, programming, study and everyday multitasking.",
        "price": "54999",
        "original_price": "64999",
        "stock": 10,
        "rating": 0,
        "review_count": 0,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1496181133206-80ce9b88a853",
    },
    {
        "name": "MacBook Air Style",
        "brand": "Apple",
        "category": "Laptops",
        "description": "A slim and lightweight premium laptop for work, study and creative tasks.",
        "price": "89999",
        "original_price": "99999",
        "stock": 7,
        "rating": 4.8,
        "review_count": 36,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1517336714731-489689fd1ca8",
    },
    {
        "name": "Gaming Laptop RTX",
        "brand": "ASUS",
        "category": "Laptops",
        "description": "A powerful gaming laptop designed for demanding games and creative workloads.",
        "price": "84999",
        "original_price": "94999",
        "stock": 6,
        "rating": 4.7,
        "review_count": 24,
        "badge": "POPULAR",
        "is_featured": True,
        "image": "photo-1593642632823-8f785ba67e45",
    },
    {
        "name": "Student Laptop",
        "brand": "Lenovo",
        "category": "Laptops",
        "description": "A practical laptop for online classes, assignments, browsing and office applications.",
        "price": "38999",
        "original_price": "44999",
        "stock": 15,
        "rating": 4.2,
        "review_count": 17,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1588872657578-7efd1f1555ed",
    },
    {
        "name": "Business Pro Laptop",
        "brand": "Dell",
        "category": "Laptops",
        "description": "A professional laptop with a clean design for business and productivity.",
        "price": "65999",
        "original_price": "72999",
        "stock": 9,
        "rating": 4.5,
        "review_count": 21,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1496181133206-80ce9b88a853",
    },
    {
        "name": "Wireless Headphones",
        "brand": "boAt",
        "category": "Headphones",
        "description": "Comfortable wireless headphones with rich sound and an immersive listening experience.",
        "price": "1499",
        "original_price": "2499",
        "stock": 25,
        "rating": 0,
        "review_count": 0,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1505740420928-5e560c06d30e",
    },
    {
        "name": "Noise Cancelling Headphones",
        "brand": "Sony",
        "category": "Headphones",
        "description": "Over-ear headphones designed to reduce background noise for focused listening.",
        "price": "3999",
        "original_price": "5499",
        "stock": 18,
        "rating": 4.6,
        "review_count": 32,
        "badge": "POPULAR",
        "is_featured": True,
        "image": "photo-1546435770-a3e426bf472b",
    },
    {
        "name": "Bluetooth Earbuds",
        "brand": "boAt",
        "category": "Headphones",
        "description": "Compact wireless earbuds for music, calls and everyday convenience.",
        "price": "1299",
        "original_price": "1999",
        "stock": 30,
        "rating": 4.3,
        "review_count": 26,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1590658268037-6bf12165a8df",
    },
    {
        "name": "Studio Sound Headset",
        "brand": "JBL",
        "category": "Headphones",
        "description": "A comfortable headset with detailed sound for entertainment and work.",
        "price": "2799",
        "original_price": "3499",
        "stock": 14,
        "rating": 4.4,
        "review_count": 15,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1583394838336-acd977736f90",
    },
    {
        "name": "Gaming Headset",
        "brand": "Logitech",
        "category": "Headphones",
        "description": "A gaming headset with cushioned ear cups and a built-in microphone.",
        "price": "2199",
        "original_price": "2999",
        "stock": 16,
        "rating": 4.5,
        "review_count": 20,
        "badge": "BESTSELLER",
        "is_featured": False,
        "image": "photo-1599669454699-248893623440",
    },
    {
        "name": "Smart Watch",
        "brand": "boAt",
        "category": "Smart Watches",
        "description": "A stylish smartwatch for everyday activity tracking and smart notifications.",
        "price": "2499",
        "original_price": "3999",
        "stock": 30,
        "rating": 0,
        "review_count": 0,
        "badge": "POPULAR",
        "is_featured": True,
        "image": "photo-1523275335684-37898b6baf30",
    },
    {
        "name": "Fitness Smart Watch",
        "brand": "Fire-Boltt",
        "category": "Smart Watches",
        "description": "A fitness-focused smartwatch with activity tracking and a modern design.",
        "price": "1799",
        "original_price": "2499",
        "stock": 22,
        "rating": 4.3,
        "review_count": 18,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1508685096489-7aacd43bd3b1",
    },
    {
        "name": "Premium AMOLED Watch",
        "brand": "Samsung",
        "category": "Smart Watches",
        "description": "A premium wearable with a vivid display and useful everyday smart features.",
        "price": "4999",
        "original_price": "6499",
        "stock": 11,
        "rating": 4.7,
        "review_count": 29,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1579586337278-3befd40fd17a",
    },
    {
        "name": "Classic Smart Band",
        "brand": "Xiaomi",
        "category": "Smart Watches",
        "description": "A lightweight smart band for daily activity and fitness monitoring.",
        "price": "999",
        "original_price": "1499",
        "stock": 35,
        "rating": 4.1,
        "review_count": 13,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1508685096489-7aacd43bd3b1",
    },
    {
        "name": "Sport Edition Watch",
        "brand": "Amazfit",
        "category": "Smart Watches",
        "description": "A sporty smartwatch with a comfortable strap and activity-focused features.",
        "price": "3299",
        "original_price": "4299",
        "stock": 14,
        "rating": 4.4,
        "review_count": 16,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1523275335684-37898b6baf30",
    },
    {
        "name": "Fast Charging Adapter",
        "brand": "Anker",
        "category": "Accessories",
        "description": "A compact charging adapter for compatible smartphones and electronic devices.",
        "price": "699",
        "original_price": "999",
        "stock": 40,
        "rating": 4.3,
        "review_count": 22,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1583863788434-e58a36330cf0",
    },
    {
        "name": "Power Bank 20000mAh",
        "brand": "Xiaomi",
        "category": "Accessories",
        "description": "A portable high-capacity power bank for charging devices while travelling.",
        "price": "1499",
        "original_price": "2199",
        "stock": 25,
        "rating": 4.5,
        "review_count": 34,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1609091839311-d5365f9ff1c5",
    },
    {
        "name": "Mechanical Keyboard",
        "brand": "Logitech",
        "category": "Accessories",
        "description": "A responsive mechanical keyboard for comfortable typing and gaming.",
        "price": "2299",
        "original_price": "2999",
        "stock": 17,
        "rating": 4.6,
        "review_count": 19,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1587829741301-dc798b83add3",
    },
    {
        "name": "Wireless Mouse",
        "brand": "Logitech",
        "category": "Accessories",
        "description": "An ergonomic wireless mouse for smooth everyday computer navigation.",
        "price": "599",
        "original_price": "899",
        "stock": 45,
        "rating": 4.2,
        "review_count": 27,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1527814050087-3793815479db",
    },
    {
        "name": "USB-C Hub Adapter",
        "brand": "UGREEN",
        "category": "Accessories",
        "description": "A useful multiport USB-C hub for connecting compatible devices and peripherals.",
        "price": "1299",
        "original_price": "1799",
        "stock": 20,
        "rating": 4.3,
        "review_count": 12,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1625842268584-8f3296236761",
    },
    {
        "name": "Bluetooth Speaker",
        "brand": "JBL",
        "category": "Other",
        "description": "A portable Bluetooth speaker for music at home, outdoors and on the go.",
        "price": "1799",
        "original_price": "2499",
        "stock": 24,
        "rating": 4.5,
        "review_count": 25,
        "badge": "BESTSELLER",
        "is_featured": True,
        "image": "photo-1608043152269-423dbba4e7e1",
    },
    {
        "name": "Digital Camera",
        "brand": "Canon",
        "category": "Other",
        "description": "A compact digital camera for capturing everyday memories and creative photography.",
        "price": "18999",
        "original_price": "22999",
        "stock": 6,
        "rating": 4.6,
        "review_count": 14,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1516035069371-29a1b244cc32",
    },
    {
        "name": "Portable Projector",
        "brand": "Epson",
        "category": "Other",
        "description": "A compact projector for enjoying movies, presentations and entertainment on a larger screen.",
        "price": "6999",
        "original_price": "8999",
        "stock": 9,
        "rating": 4.2,
        "review_count": 11,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1478720568477-152d9b164e26",
    },
    {
        "name": "Home Security Camera",
        "brand": "TP-Link",
        "category": "Other",
        "description": "A home monitoring camera for keeping an eye on your living space.",
        "price": "2499",
        "original_price": "3299",
        "stock": 18,
        "rating": 4.4,
        "review_count": 16,
        "badge": "NEW",
        "is_featured": False,
        "image": "photo-1753108140127-afc3e215d75b",
    },
    {
        "name": "Smart Home Speaker",
        "brand": "Amazon",
        "category": "Other",
        "description": "A compact smart home speaker for convenient audio and connected-home use.",
        "price": "3499",
        "original_price": "4499",
        "stock": 13,
        "rating": 4.3,
        "review_count": 10,
        "badge": "POPULAR",
        "is_featured": False,
        "image": "photo-1543512214-318c7553f230",
    },
]


class Command(BaseCommand):
    help = "Seed Kobo Goods with 30 demo products, brands and product images"

    def handle(self, *args, **options):
        created_count = 0
        existing_count = 0
        image_count = 0
        image_failures = []

        with transaction.atomic():
            for data in PRODUCTS:
                product_data = data.copy()
                image_id = product_data.pop("image")

                product_name = product_data["name"]

                defaults = {
                    "brand": product_data["brand"],
                    "category": product_data["category"],
                    "description": product_data["description"],
                    "price": Decimal(product_data["price"]),
                    "original_price": Decimal(product_data["original_price"]),
                    "stock": product_data["stock"],
                    "rating": product_data["rating"],
                    "review_count": product_data["review_count"],
                    "badge": product_data["badge"],
                    "is_featured": product_data["is_featured"],
                }

                product, created = Product.objects.get_or_create(
                    name=product_name,
                    defaults=defaults,
                )

                if created:
                    created_count += 1
                else:
                    existing_count += 1

                    product.brand = product_data["brand"]
                    product.is_featured = product_data["is_featured"]

                    product.save(
                        update_fields=["brand", "is_featured"]
                    )

                if not product.image:
                    image_url = (
                        f"https://images.unsplash.com/{image_id}"
                        "?auto=format&fit=crop&w=800&h=800&q=85"
                    )

                    try:
                        image_request = Request(
                            image_url,
                            headers={
                                "User-Agent": "KoboGoodsProductSeeder/1.0"
                            },
                        )

                        with urlopen(image_request, timeout=20) as response:
                            image_data = response.read()

                        filename = f"{product.id}-{image_id}.jpg"

                        product.image.save(
                            filename,
                            ContentFile(image_data),
                            save=True,
                        )

                        image_count += 1

                    except (
                        URLError,
                        HTTPError,
                        TimeoutError,
                        OSError,
                        ValueError,
                    ) as error:
                        image_failures.append(
                            f"{product.name}: {error}"
                        )

                self.stdout.write(
                    f"{'Created' if created else 'Updated'}: "
                    f"{product.brand} - {product.name}"
                )

        total_count = Product.objects.count()
        featured_count = Product.objects.filter(
            is_featured=True
        ).count()

        self.stdout.write(self.style.SUCCESS(
            f"Finished successfully.\n"
            f"New products created: {created_count}\n"
            f"Existing products updated: {existing_count}\n"
            f"Images downloaded: {image_count}\n"
            f"Featured products: {featured_count}\n"
            f"Total products in database: {total_count}"
        ))

        if image_failures:
            self.stdout.write(self.style.WARNING(
                f"{len(image_failures)} product image(s) could not be downloaded:"
            ))

            for failure in image_failures:
                self.stdout.write(self.style.WARNING(failure))

            self.stdout.write(
                "You can upload missing images later through Django Admin."
            )
