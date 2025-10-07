from pydantic import BaseModel
from typing import List


class Supplier(BaseModel):
    name: str
    category: str
    avg_rating: float
    reviews: str


class RecommendRequest(BaseModel):
    user_prompt: str
    suppliers: List[Supplier]


class SupplierCredential(BaseModel):
    external_id: str
    net_amount: float
    payer_email: str
    payment_method: str


class InvoiceResponse(BaseModel):
    data: dict
    invoice_url: str


class StatusResponse(BaseModel):
    status: str


class PayoutCredential(BaseModel):
    reference_id: str
    channel_code: str
    account_holder_name: str
    account_number: str
    amount: int
