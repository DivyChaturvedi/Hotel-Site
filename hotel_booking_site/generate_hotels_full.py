import os
import csv
import random
import requests
import pandas as pd
from PIL import Image
from io import BytesIO

# 📁 Step 1: Folder setup
hotel_img_folder = "media/hotels"
room_img_folder = "media/rooms"
os.makedirs(hotel_img_folder, exist_ok=True)
os.makedirs(room_img_folder, exist_ok=True)

# 🔑 Step 2: Your Pexels API Key (put your valid key here)
PEXELS_API_KEY = "OH2H9xLwL638EBXx4xs6iK15S8wvrFVGm6xX8QjA3YLOwOsxFA11kpGH"
headers = {"Authorization": PEXELS_API_KEY}

# 🏨 Room types
room_types = ["Standard", "Deluxe", "Suite"]

# 🔤 Slugify (safe filenames)
def slugify(text):
    text = text.lower().replace(" ", "_")
    return "".join(c for c in text if c.isalnum() or c == "_")

# 🧹 Step 3: Clean CSV (remove Image URL)
def clean_csv(input_file="hotels.csv", output_file="hotels_clean.csv"):
    print("🧹 Cleaning hotels.csv ...")
    df = pd.read_csv(input_file)
    if "Image URL" in df.columns:
        df = df.drop(columns=["Image URL"])
        print("✅ 'Image URL' column removed.")
    df.to_csv(output_file, index=False)
    print(f"✅ Clean CSV saved as '{output_file}'")
    return output_file

# 🖼️ Step 4: Download or placeholder
def download_image(url, path):
    try:
        response = requests.get(url, timeout=15)
        if response.status_code == 200:
            img = Image.open(BytesIO(response.content))
            img.save(path)
            print(f"✅ Downloaded: {path}")
        else:
            raise Exception("Bad response")
    except Exception as e:
        img = Image.new("RGB", (400, 300), (random.randint(0,255), random.randint(0,255), random.randint(0,255)))
        img.save(path)
        print(f"⚠️ Placeholder created for {path}")

# 🔍 Step 5: Fetch random image from Pexels
def fetch_random_image(query):
    try:
        url = f"https://api.pexels.com/v1/search?query={query}&per_page=15"
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            data = response.json()
            photos = data.get("photos", [])
            if photos:
                chosen = random.choice(photos)
                return chosen["src"]["original"]
    except Exception as e:
        print("❌ Pexels error:", e)
    return None

# 🏨 Step 6: Process hotels
def process_hotels(csv_file):
    hotels = []
    with open(csv_file, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            hotels.append({
                "name": row["Name"],
                "city": row["City"],
                "address": row["Address"],
                "rating": row["Rating"],
                "price": row["Price (INR)"],
                "rooms": row["Rooms vailable"],
                "amenities": row["Amenities"]
            })

    print(f"🏨 Found {len(hotels)} hotels. Starting image downloads...")

    for hotel in hotels:
        slug = slugify(hotel["name"])
        img_name = f"{slug}_1.jpg"
        img_path = os.path.join(hotel_img_folder, img_name)

        query = f"{hotel['name']} {hotel['city']} hotel luxury"
        img_url = fetch_random_image(query)
        if not img_url:
            img_url = fetch_random_image(f"{hotel['city']} hotel view")

        if img_url:
            download_image(img_url, img_path)
        else:
            download_image("", img_path)

    return hotels

# 🏩 Step 7: Generate room images + rooms.csv
def process_rooms(hotels):
    with open("rooms.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["hotel_name", "room_type", "price", "quantity", "description", "image_name"])

        for hotel in hotels:
            slug_hotel = slugify(hotel["name"])
            for rtype in room_types:
                price = random.randint(2000, 8000)
                quantity = random.randint(3, 8)
                desc = f"{rtype} room with modern facilities at {hotel['name']}."
                img_name = f"{slug_hotel}_{slugify(rtype)}_1.jpg"
                img_path = os.path.join(room_img_folder, img_name)

                query = f"{rtype} room {hotel['city']} interior design"
                img_url = fetch_random_image(query)
                if not img_url:
                    img_url = fetch_random_image(f"{rtype} hotel room {hotel['city']}")

                if img_url:
                    download_image(img_url, img_path)
                else:
                    download_image("", img_path)

                writer.writerow([hotel["name"], rtype, price, quantity, desc, img_name])

    print("✅ rooms.csv created successfully!")

# 🚀 Step 8: Run all steps
def main():
    clean_file = clean_csv("hotels.csv", "hotels_clean.csv")
    hotels = process_hotels(clean_file)
    process_rooms(hotels)
    print("\n🎉 All done! Real images generated for hotels & rooms.")
    print("📁 Check folders: media/hotels & media/rooms")

if __name__ == "__main__":
    main()
