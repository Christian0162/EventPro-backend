import google.generativeai as genai
import os
from typing import List
from models.schemas import Supplier
from dotenv import load_dotenv

load_dotenv()


class GeminiService:

    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError("Missing GEMINI_API_KEY in environment")
        genai.configure(
            api_key=api_key,
            client_options={
                "api_endpoint": "https://us-central1-aiplatform.googleapis.com"
            },
        )

        self.model = genai.GenerativeModel("gemini-2.0-flash")

    def get_recommendations(self, user_prompt: str, suppliers: List[Supplier]) -> str:
        suppliers_text = "\n".join(
            f"{s.name} ({s.category}): {s.avg_rating}/5 – {s.reviews}"
            for s in suppliers
        )

        prompt = f"""`
            You are an intelligent assistant that recommends suppliers to event planners. The way you talk make it like a human    

            User wants: {user_prompt}

            Here is the list of suppliers:
            {suppliers_text}

            Based on reviews, ratings, and category match, suggest the top 3 most suitable
            suppliers with a short explanation for each.

            the following format must be like this:
            1: "Supplier name", Details and just say supplier profiles
            """.strip()
        response = self.model.generate_content(prompt)
        return response.text
