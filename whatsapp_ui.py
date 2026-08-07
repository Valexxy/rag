CURRENCY_MAP = {
    "NGN": "₦",
    "USD": "$",
    "EUR": "€",
    "GBP": "£",
    "KES": "KSh ",
    "GHS": "₵",
    "INR": "₹",
    "AED": "AED ",
    "CAD": "CA$",
    "BRL": "R$"
}

def format_currency(amount: float, currency_code: str = "NGN") -> str:
    """Formats amount with appropriate currency symbol worldwide."""
    symbol = CURRENCY_MAP.get((currency_code or "NGN").upper(), f"{currency_code} ")
    return f"{symbol}{amount:,.2f}"

def render_executive_whatsapp_dashboard(tenant: dict, revenue_today: float = 485000.0, active_leads: int = 42, closed_deals: int = 12, waybills_active: int = 5) -> str:
    """Renders high-converting ASCII Executive Command Dashboard for business owner WhatsApp."""
    b_name = tenant.get("business_name", "Valexxy Global Store")
    currency = tenant.get("currency", "NGN")
    rev_str = format_currency(revenue_today, currency)

    return f"""📊 *[{b_name.upper()} - EXECUTIVE DASHBOARD]*
---------------------------------------------
💰 *Revenue Today:* {rev_str}
👥 *Active Leads Today:* {active_leads}
✅ *Closed Deals:* {closed_deals}
🚚 *Active Waybills:* {waybills_active}
🤖 *AI Autopilot Status:* ACTIVE (96.4% zero-cost)

⚡ *Quick Owner Commands:*
• `#add Item | Price | Desc` - Add item/service
• `#broadcast Message` - Send customer broadcast
• `#staff add +phone role` - Delegate staff access
• `#unmute +phone` - Resume bot for customer

🌐 *Web Dashboard:* https://commerce-ai-saas.onrender.com/dashboard"""

def render_role_based_menu(role: str, tenant: dict, customer_phone: str) -> str:
    """Renders interactive role-based menu for WhatsApp users."""
    b_name = tenant.get("business_name", "Valexxy Global Store")
    
    if role == "OWNER" or role == "SUPER_ADMIN":
        return render_executive_whatsapp_dashboard(tenant)
    
    # Default Client / Customer Menu
    return f"""🤖 *Welcome to [{b_name}] Automated Service!*

How can we assist you today? Please reply with a number or keyword:

1️⃣ *Catalog & Products* - View current prices & items
2️⃣ *Book Service / Tour* - Schedule an appointment or inspection
3️⃣ *Track Order / Waybill* - Check status of your shipment
4️⃣ *My Account & Rewards* - View balance & cashback
5️⃣ *Human Support* - Speak with an executive manager

_Reply 1, 2, 3, 4, or 5 to proceed!_"""
