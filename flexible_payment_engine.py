class FlexiblePaymentEngine:
    """Flexible Merchant Payment Details & Zero-False-Validation Receipt Guard."""

    @staticmethod
    def format_merchant_payment_instructions(tenant: dict, amount: float, reference: str) -> str:
        """Formats merchant's preferred bank details or payment link without forcing automated gateways."""
        b_name = tenant.get("business_name", "Teeslux Global Store")
        bank_name = tenant.get("bank_name", "Access Bank")
        account_num = tenant.get("account_number", "0252796240")
        account_name = tenant.get("account_name", b_name)
        currency = tenant.get("currency", "NGN")

        return f"""💳 *[{b_name} - VERIFIED PAYMENT DETAILS]*
---------------------------------------------
💰 *Amount Due:* ₦{amount:,.2f} {currency}
🏷️ *Payment Reference:* `{reference}`

🏦 *BANK TRANSFER INSTRUCTIONS:*
• *Bank Name:* {bank_name}
• *Account Number:* `{account_num}`
• *Account Name:* {account_name}

---------------------------------------------
👉 *After Transfer:*
Please send your payment receipt screenshot or transfer reference here. 

🛡️ *Safety Guarantee:* For your protection and ours, all payment receipts undergo manual 1-click verification by our finance manager before order dispatch!"""

    @staticmethod
    def process_receipt_screenshot_safely(customer_phone: str, reference: str) -> dict:
        """Processes receipt screenshot without false automated validation. Subject to manual manager confirmation."""
        return {
            "status": "PENDING_MANAGER_VERIFICATION",
            "reply": f"""🧾 *[RECEIPT RECEIVED - PENDING MANAGER CONFIRMATION]*
---------------------------------------------
📱 *Customer:* `{customer_phone}`
🏷️ *Reference:* `{reference}`
⚡ *Status:* `PENDING MANAGER BANK APP VERIFICATION`

Our store manager has been notified to verify the transfer in our bank app. As soon as confirmed, your order dispatch status will be updated immediately!"""
        }

flexible_payment = FlexiblePaymentEngine()
