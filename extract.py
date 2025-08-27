import os
import requests
import pandas as pd
from duckduckgo_search import DDGS

# Load your Excel file with drug names
df = pd.read_csv("shortlist.csv")

df = df.tail(50)

# Folder to save images
output_folder = "scraped_images"
os.makedirs(output_folder, exist_ok=True)

# Initialize DuckDuckGo search
with DDGS() as ddgs:
    for index, row in df.iterrows():
        product = row['drug']
        query = f"{product} back of tablet"
        print(f"🔍 Searching for {query}")

        # Get up to 3 images only
        results = ddgs.images(query, max_results=1)

        safe_name = product[:30].replace('/', '').replace(' ', '_')

        for i, result in enumerate(results):
            try:
                img_url = result["image"]
                img_data = requests.get(img_url, timeout=10).content
                filename = f"{output_folder}/{safe_name}_{i}.jpg"
                with open(filename, "wb") as f:
                    f.write(img_data)
                print(f"✅ Saved {filename}")
            except Exception as e:
                print(f"❌ Error downloading image: {e}")

print("🎉 Test run complete. Images saved in:", output_folder)
