from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv()

# ─── Configure Gemini ─────────────────────────────────────────────────────
API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("Missing GEMINI_API_KEY in environment")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.0-flash")

# ─── FastAPI Setup ─────────────────────────────────────────────────────────
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://your-frontend-domain.com",    # your real frontend URL
        "https://admin.your-frontend-domain.com"  # maybe admin panel or staging
    ],
    allow_methods=["GET", "POST", "PUT", "DELETE"],  # only what you need
    allow_headers=["Authorization", "Content-Type"],  # only needed headers
    allow_credentials=True,
)


class Supplier(BaseModel):
    name: str
    category: str
    avg_rating: float
    reviews: str

class RecommendRequest(BaseModel):
    user_prompt: str
    suppliers: List[Supplier]

@app.post("/recommend")
async def recommend_suppliers(req: RecommendRequest):
    try:
        suppliers_text = "\n".join(
            f"{s.name} ({s.category}): {s.avg_rating}/5 – {s.reviews}"
            for s in req.suppliers
        )

        prompt = f"""`
You are an intelligent assistant that recommends suppliers to event planners. The way you talk make it like a human    

User wants: {req.user_prompt}

Here is the list of suppliers:
{suppliers_text}

Based on reviews, ratings, and category match, suggest the top 3 most suitable
suppliers with a short explanation for each.

the following format must be like this:
1: "Supplier name", Details
""".strip()

        response = model.generate_content(prompt)
        return { "recommendations": response.text }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))