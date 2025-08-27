import os
import requests
import pandas as pd

API_KEY = 'af616f97d7f628b811a4f8ba7eacf2ee4b345fcecb454114388f95f08feab023'  # Get this from https://serpapi.com

df = pd.read_excel("products_cleaned.xlsx")
output_folder = "images"
os.makedirs(output_folder, exist_ok=True)

for index, row in df.iterrows():
    product = row['product_name']
    query = f"{product} back of tablet"
    print(f"🔍 Searching for {query}")

    params = {
        "engine": "google",
        "q": query,
        "tbm": "isch",
        "api_key": API_KEY
    }

    response = requests.get("https://serpapi.com/search", params=params)
    results = response.json()

    if 'images_results' in results:
        for i, image in enumerate(results['images_results'][:5]):
            try:
                img_url = image['original']
                img_data = requests.get(img_url, timeout=10).content
                safe_name = product[:30].replace('/', '').replace(' ', '')
                with open(f"{output_folder}/{safe_name}_{i}.jpg", 'wb') as f:
                    f.write(img_data)
                print(f"✅ Saved image {i+1}")
            except Exception as e:
                print(f"❌ Error downloading image: {e}")
    else:
        print("⚠️ No images found.")

print("🎉 Done.")
