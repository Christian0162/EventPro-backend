from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import payout, recommendations, payments

app = FastAPI()

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(payout.router)
app.include_router(recommendations.router)
app.include_router(payments.router)

@app.get("/")
async def root():
    return {"message": "Welcome to the Supplier Recommendation API"}