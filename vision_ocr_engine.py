import re

class VisionOCREngine:
    """Image & Receipt Visual Analyzer for Bank Transfer Screenshots."""

    @staticmethod
    def parse_payment_receipt_text(ocr_text: str) -> dict:
        """Extracts bank name, transaction reference, and amount from receipt screenshot OCR text."""
        text = ocr_text.upper()
        
        # Extract transaction reference (e.g. TRX98127391 or 0252796240)
        ref_match = re.search(r'\b(TRX\d+|\d{10,12})\b', text)
        txn_ref = ref_match.group(0) if ref_match else "TRX-VERIFIED-IMG"

        # Extract amount (e.g. N25,000 or 25000.00)
        amt_match = re.search(r'(?:N|NGN|\$)?\s*([\d,]+\.?\d*)', text)
        amount = 0.0
        if amt_match:
            try:
                amount = float(amt_match.group(1).replace(",", ""))
            except Exception:
                amount = 0.0

        return {
            "status": "PARSED",
            "transaction_reference": txn_ref,
            "extracted_amount": amount,
            "is_valid_format": bool(ref_match)
        }

vision_ocr = VisionOCREngine()
