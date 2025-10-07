from services.gemini_service import GeminiService
from services.payment_service import PaymentService
from services.payout_service import PayoutService


def get_gemini_service():
    return GeminiService()


def get_payment_service():
    return PaymentService()


def get_payout_service():
    return PayoutService()
