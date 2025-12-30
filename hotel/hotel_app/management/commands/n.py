import random
from django.core.management.base import BaseCommand
from cloudinary.uploader import upload
from hotel_app.models import Hotel

class Command(BaseCommand):
    help = "Assign random images from internet to hotels via Cloudinary"

    def handle(self, *args, **kwargs):
        # List of random hotel images (Unsplash free images)
        hotel_image_urls = [
            
                "https://images.unsplash.com/photo-1551782450-a2132b4ba21d",
    "https://images.unsplash.com/photo-1501117716987-c8e4f9dc37c1",
    "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
        "https://images.unsplash.com/photo-1560347876-aeef00ee58a1",
    "https://images.unsplash.com/photo-1576671088942-785c8d2be94e",
    "https://images.unsplash.com/photo-1560448204-3b64a6ae5855",
    "https://images.unsplash.com/photo-1582719478250-c3ed7c22e2b3",
    "https://images.unsplash.com/photo-1600585154340-be6161a56a0c",
        ]

        hotels = Hotel.objects.all()
        total = hotels.count()
        self.stdout.write(f"Found {total} hotels. Assigning images...")

        for hotel in hotels:
            url = random.choice(hotel_image_urls)
            try:
                uploaded = upload(url, folder="hotel_images")
                hotel.image = uploaded['public_id']
                hotel.save()
                self.stdout.write(self.style.SUCCESS(f"✅ {hotel.name} updated"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"❌ {hotel.name} failed: {e}"))

        self.stdout.write(self.style.SUCCESS("All done!"))
