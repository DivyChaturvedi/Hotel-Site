import os
import csv
import random
import requests
from PIL import Image
from io import BytesIO

# ------------------ Config ------------------
PEXELS_API_KEY = 'OH2H9xLwL638EBXx4xs6iK15S8wvrFVGm6xX8QjA3YLOwOsxFA11kpGH'  # <-- apni key yaha daal
headers = {"Authorization": PEXELS_API_KEY}

hotel_img_folder = "media/hotels"
room_img_folder = "media/rooms"
os.makedirs(hotel_img_folder, exist_ok=True)
os.makedirs(room_img_folder, exist_ok=True)

# ------------------ Helper ------------------
def slugify(text):
    text = text.lower().replace(" ", "_")
    return "".join(c for c in text if c.isalnum() or c == "_")

def download_image(url, path):
    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(path)
            print(f"✅ Downloaded: {path}")
        else:
            raise Exception("Failed to download")
    except Exception as e:
        print(f"⚠️ Error: {e} — using placeholder.")
        img = Image.new("RGB", (400, 300), (
            random.randint(0,255),
            random.randint(0,255),
            random.randint(0,255)
        ))
        img.save(path)

def fetch_pexels_image(query):
    url = f"https://api.pexels.com/v1/search?query={query}&per_page=1"
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["photos"]:
            return data["photos"][0]["src"]["original"]
    return None

# ------------------ 1️⃣ Process Hotels ------------------
with open("mp_hotels.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    hotels = list(reader)

with open("hotels_with_images.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = list(hotels[0].keys()) + ["image_name"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for hotel in hotels:
        name = hotel["Hotel Name"]
        city = hotel["City"]
        slug = slugify(name)
        img_name = f"{slug}_hotel.jpg"
        img_path = os.path.join(hotel_img_folder, img_name)

        query = f"{name} {city} hotel exterior"
        img_url = fetch_pexels_image(query)
        if img_url:
            download_image(img_url, img_path)
        else:
            download_image("", img_path)

        hotel["image_name"] = img_name
        writer.writerow(hotel)

print("\n🏨 All hotel images saved successfully!\n")

# ------------------ 2️⃣ Process Rooms ------------------
with open("rooms.csv", newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rooms = list(reader)

with open("rooms_with_images.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = list(rooms[0].keys())
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()

    for room in rooms:
        hotel_name = room["hotel_name"]
        room_type = room["room_type"]
        slug = slugify(f"{hotel_name}_{room_type}")
        img_name = f"{slug}.jpg"
        img_path = os.path.join(room_img_folder, img_name)

        query = f"{hotel_name} {room_type} room interior"
        img_url = fetch_pexels_image(query)
        if img_url:
            download_image(img_url, img_path)
        else:
            download_image("", img_path)

        room["image_name"] = img_name
        writer.writerow(room)

print("🚪 All room images saved successfully!\n")
print("🎉 Done — images stored in media/hotels and media/rooms.")
