import os
import csv
import random
import requests
from PIL import Image
from io import BytesIO

# Folders
hotel_img_folder = "media/hotels"
room_img_folder = "media/rooms"
os.makedirs(hotel_img_folder, exist_ok=True)
os.makedirs(room_img_folder, exist_ok=True)

# Pexels API Key
PEXELS_API_KEY = 'OH2H9xLwL638EBXx4xs6iK15S8wvrFVGm6xX8QjA3YLOwOsxFA11kpGH'
headers = {'Authorization': PEXELS_API_KEY}

# Room types
room_types = ["Standard", "Deluxe", "Suite"]

# Cities list (use as fallback if CSV doesn't have city)
cities = ["Goa", "Udaipur", "Manali", "Jaipur", "Mumbai", "Munnar", "Bangalore", "Rishikesh", "Pondicherry", "Jaisalmer"]

# Slug function for filenames
def slugify(text):
    text = text.lower().replace(" ", "_")
    return ''.join(c for c in text if c.isalnum() or c == '_')

# Download image or generate placeholder
def download_image(url, path):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(path)
            print(f"Downloaded {path}")
        else:
            raise Exception("Failed to retrieve image")
    except Exception as e:
        print(f"Error downloading {url}: {e}")
        # Placeholder image
        img = Image.new("RGB", (400, 300), (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        img.save(path)
        print(f"Placeholder {path}")

# Fetch image from Pexels
def fetch_pexels_image(query):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data['photos']:
            return data['photos'][0]['src']['original']
    return None

# ------------------- Read all hotels -------------------
hotels = []
with open("mp_hotels.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        hotels.append({
                "name": row["Hotel Name"],
                "city": row["City"],
                "address": row["Address"],
                "rating": row["Rating"],
                "price": row["Price (INR)"],
                "rooms": row["Rooms Available"],
                "amenities": row["Amenities"]
        })

# ------------------- Generate hotels.csv -------------------
with open("mp_hotels.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["name", "city", "address", "description", "hotel_images"])
    for hotel in hotels:
        slug = slugify(hotel['name'])
        img_name = f"{slug}_1.jpg"
        img_url = fetch_pexels_image(f"hotel {hotel['name']} {hotel['city']}")
        if img_url:
            download_image(img_url, os.path.join(hotel_img_folder, img_name))
        writer.writerow([hotel['name'], hotel['city'], hotel['address'], hotel['rating'],hotel['price'],hotel['rooms'],hotel['amenities'], img_name])

# ------------------- Generate rooms.csv -------------------
with open("rooms.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["hotel_name", "room_type", "price", "quantity", "description", "image_name"])
    for hotel in hotels:
        slug_hotel = slugify(hotel['name'])
        for rtype in room_types:
            price = random.randint(2000, 6000)
            quantity = random.randint(2, 5)
            description = f"{rtype} room with all modern amenities."
            slug_room = slugify(rtype)
            img_name = f"{slug_hotel}_{slug_room}_1.jpg"
            img_url = fetch_pexels_image(f"{hotel['name']} {rtype} room")
            if img_url:
                download_image(img_url, os.path.join(room_img_folder, img_name))
            writer.writerow([hotel['name'], rtype, price, quantity, description, img_name])

print("✅ All hotels and rooms processed with images and CSVs!")
