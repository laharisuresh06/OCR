import pandas as pd

# Load the dataset
df = pd.read_csv("new_data.csv")

# Show available columns
print("Columns:", df.columns.tolist())

# Extract salts
if "salt_composition" in df.columns:
    salts = df["salt_composition"].dropna().unique()
    salts = [s.strip() for s in salts if isinstance(s, str)]
else:
    raise ValueError("❌ No 'salt_composition' column found!")

# Extract product names (if needed)
if "product_name" in df.columns:
    product_names = df["product_name"].dropna().unique()
    product_names = [p.strip() for p in product_names if isinstance(p, str)]
else:
    product_names = []

# Combine salts and product names → to increase count
combined_list = list(set(salts + product_names))

print(f"✅ Found {len(combined_list)} unique drugs/salts")

# If we want at least 3000 rows, expand artificially
target = 3000
multiplied = []
while len(multiplied) < target:
    multiplied.extend(combined_list)

final_list = multiplied[:target]

# Save to CSV
pd.DataFrame(final_list, columns=["drug"]).to_csv("shortlist.csv", index=False)
print(f"✅ Shortlist saved as shortlist.csv with {len(final_list)} rows")
