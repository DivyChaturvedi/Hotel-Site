import os
import csv
from django.core.management.base import BaseCommand
from hotel_app.models import Hotel
from django.conf import settings


class Command(BaseCommand):
    help = "Delete old hotels and import new ones from mp_hotels.csv"

    def handle(self, *args, **options):
        # CSV ka path
        hotels_file = os.path.join(settings.BASE_DIR, "mp_hotels.csv")

        if not os.path.exists(hotels_file):
            self.stdout.write(self.style.ERROR(f"❌ CSV not found at {hotels_file}"))
            return

        # 🔥 Purane hotels delete
        Hotel.objects.all().delete()
        self.stdout.write(self.style.WARNING("⚠️ All existing hotels deleted."))

        with open(hotels_file, newline='', encoding="utf-8") as file:
            reader = csv.DictReader(file)
            self.stdout.write(self.style.WARNING(f"CSV Headers: {reader.fieldnames}"))

            count = 0
            for row in reader:
                try:
                    hotel = Hotel.objects.create(
                        name=row['Name'].strip(),
                        city=row['City'].strip(),
                        address=row['Address'].strip(),
                        rating=float(row['Rating'].strip()) if row['Rating'].strip() else None,
                        price=row['Price (INR)'].strip(),
                        rooms_available=int(row['Rooms vailable'].strip()) if row['Rooms vailable'].strip() else 0,
                        amenities=row['Amenities'].strip(),
                        image=row['Image URL'].strip() if row.get('Image URL') else None
                    )
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f"✅ Added: {hotel.name} ({hotel.city})"))

                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"❌ Error importing hotel: {str(e)}"))

        self.stdout.write(self.style.SUCCESS(f"\n🎉 Successfully imported {count} hotels from mp_hotels.csv"))
