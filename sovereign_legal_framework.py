from datetime import datetime

class SovereignLegalFrameworkEngine:
    """Enterprise Legal Compliance, GDPR/NDPR Data Protection & Universal Liability Shield Engine."""

    LEGAL_DISCLAIMERS = {
        "market_price": "⚖️ *LEGAL DISCLAIMER:* Real-time market commodity prices are 24-hour verified spot indicators. Final invoice issued by verified merchant governs settlement.",
        "offline_payment": "🛡️ *FINANCIAL NOTICE:* Bank transfer references are cryptographically verified pending 1-click manual manager bank app confirmation. No false automated validations.",
        "data_privacy": "🔐 *DATA PROTECTION NOTICE (NDPR/GDPR):* Your phone number & order data are encrypted and strictly isolated for this business only. Zero data selling to third parties.",
        "terms_of_service": "📜 *TERMS OF SERVICE:* By interacting with this automated system, you agree to our 1-Fixed Price Policy and Verified Merchant Directory Terms."
    }

    def get_onboarding_consent_card(self, business_name: str) -> str:
        """Generates legal onboarding consent card sent to new users on first interaction."""
        return f"""⚖️ *[TERMS OF SERVICE & DATA PROTECTION CONSENT]*
---------------------------------------------
Welcome to *{business_name}* Automated Assistant!

🔒 *YOUR DATA RIGHTS (NDPR / GDPR COMPLIANT):*
• 100% Strict Tenant Data Isolation.
• Your data is used exclusively to fulfill your orders.
• Reply `#gdpr-erase` anytime to request complete data deletion.
• Reply `#gdpr-export` to receive a copy of your chat & order records.

📜 *1-FIXED PRICE POLICY:* All catalog prices are fixed at 1 single price for top quality guarantee. Discount inquiries are automatically routed to our human store manager.

---------------------------------------------
By replying or querying this bot, you accept our Terms of Service & Privacy Policy."""

    def get_full_legal_terms_html(self) -> str:
        """Renders comprehensive web legal terms & privacy policy page for /legal."""
        now_str = datetime.now().strftime("%B %d, %Y")
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Legal Terms of Service & Privacy Policy | Sovereign AI Commerce</title>
    <style>
        body {{ font-family: sans-serif; background: #07090e; color: #f0f4f8; padding: 40px; line-height: 1.6; max-width: 900px; margin: 0 auto; }}
        h1, h2 {{ color: #00f2fe; }}
        .card {{ background: rgba(13, 17, 26, 0.9); border: 1px solid rgba(0, 242, 254, 0.2); padding: 24px; border-radius: 16px; margin-bottom: 24px; }}
    </style>
</head>
<body>
    <h1>📜 Legal Framework & Privacy Policy</h1>
    <p>Last Updated: {now_str}</p>
    
    <div class="card">
        <h2>1. Data Protection & Privacy (NDPR & GDPR Compliance)</h2>
        <p>Sovereign AI Commerce enforces 100% strict multi-tenant isolation. Customer data is encrypted at rest using AES-256 and in transit using TLS 1.3. We never sell, rent, or monetize user data.</p>
        <p>Users maintain full sovereignty over their data, including the right to complete erasure (#gdpr-erase) and data portability (#gdpr-export).</p>
    </div>

    <div class="card">
        <h2>2. Fixed 1-Price Guarantee & Bargaining Policy</h2>
        <p>All catalog prices listed on tenant stores are set at 1 fixed price for top quality guarantee. Any request for price negotiations or discounts is automatically routed to the human store manager.</p>
    </div>

    <div class="card">
        <h2>3. Offline Payment & Zero-False-Validation Shield</h2>
        <p>Bank transfer receipts and payment references submitted to the system undergo zero false automated validation. Payments are flagged as pending manual bank app settlement by the merchant owner.</p>
    </div>
</body>
</html>"""

sovereign_legal = SovereignLegalFrameworkEngine()
