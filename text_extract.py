# filename: ocr_api.py
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import cv2
import easyocr
import numpy as np
import re
import pandas as pd
from rapidfuzz import process, fuzz

app = FastAPI()

# -------------------------------
# Event: Show docs link on startup
# -------------------------------
@app.on_event("startup")
async def startup_event():
    print("\n🚀 Server is running!")
    print("📌 Open API docs here: http://127.0.0.1:8000/docs\n")

# -------------------------------
# Home Route
# -------------------------------
@app.get("/")
def home():
    return {"message": "Go to /docs for API documentation"}

# -------------------------------
# Allow frontend requests (CORS)
# -------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # change to ["http://localhost:3000"] for React frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------------------
# Load EasyOCR model once globally
# -------------------------------
reader = easyocr.Reader(['en'])

# -------------------------------
# Load Drug Database
# -------------------------------
drug_df = pd.read_csv("new_data.csv")  
# Expected columns: product_name, salt_composition, medicine_desc, side_effects, drug_interactions

# -------------------------------
# Utility: Clean extracted text
# -------------------------------
def clean_text(text: str) -> str:
    text = text.lower()
    text = re.sub(r'[^a-z0-9\s]', '', text)  # keep only alphanumeric and space
    text = re.sub(r'\s+', ' ', text).strip()  # collapse multiple spaces
    return text

# -------------------------------
# Utility: Match OCR text to drug
# -------------------------------
def match_drug(ocr_text, drug_df, top_n=1):
    choices = drug_df["product_name"].astype(str).tolist()
    
    results = process.extract(
        ocr_text,
        choices,
        scorer=fuzz.token_sort_ratio,
        limit=top_n
    )
    
    if not results:
        return None
    
    best_match, score, index = results[0]
    matched_row = drug_df.iloc[index].to_dict()
    
    return matched_row

# -------------------------------
# OCR Endpoint
# -------------------------------
@app.post("/ocr/")
async def process_image(file: UploadFile = File(...)):
    try:
        # Read uploaded image into numpy array
        contents = await file.read()
        np_arr = np.frombuffer(contents, np.uint8)
        img = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

        # Run OCR
        results = reader.readtext(img)

        # Extract + clean text
        extracted_texts = [clean_text(res[1]) for res in results if res[1].strip()]
        final_text = " ".join(extracted_texts)

        # Match drug from database
        matched_drug = match_drug(final_text, drug_df)

        if not matched_drug:
            return {
                "filename": file.filename,
                "matched_drug": "No match found"
            }

        return {
            "matched_drug": {
                "product_name": matched_drug.get("product_name", ""),
                "salt_composition": matched_drug.get("salt_composition", ""),
                "description": matched_drug.get("medicine_desc", ""),
                "side_effects": matched_drug.get("side_effects", "")
            }
        }

    except Exception as e:
        return {"error": str(e)}

# -------------------------------
# Run Server
# -------------------------------
if __name__ == "__main__":
    uvicorn.run("ocr_api:app", host="127.0.0.1", port=8000, reload=True)
