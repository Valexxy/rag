"""
====================================================================
UNIVERSAL MULTI-NICHE GLOBAL BUSINESS ENGINE (v2030)
====================================================================
Extends AI Commerce & Customer Care across ALL global business sectors:
1. RETAIL & E-COMMERCE (Products, Specs, Prices, Cart)
2. REAL ESTATE (Property Listings, Inspections, Lease Agreements)
3. HEALTHCARE & CLINICS (Doctor Appointments, Consultations, Refills)
4. HOSPITALITY & HOTELS (Room Booking, Check-In, Concierge)
5. BEAUTY & SPA (Hair Installation, Nails, Massage Appointments)
6. AUTOMOBILE & AUTO REPAIR (Car Maintenance, Parts, Test Drives)
7. PROFESSIONAL & LEGAL SERVICES (Consultations, Case Filing, Retainers)
8. EDUCATION & ACADEMIES (Course Admissions, Timetables, Tuition)
9. RESTAURANTS & CATERING (Food Menu, Table Reservation, Delivery)
10. TRAVEL & LOGISTICS (Flights, Visas, Cargo Tracking, Waybills)
"""

from typing import Dict, Any, List


class MultiNicheEngine:
    """Universal Business Domain Formatter Engine."""

    @staticmethod
    def format_niche_greeting(biz_name: str, niche: str, tod_greeting: str, formatted_time: str, is_returning: bool = False, last_item: str = "") -> str:
        niche = (niche or "retail").lower()

        niche_configs = {
            "real_estate": {
                "title": "GRA Prime Properties & Estates",
                "tagline": "Premium Real Estate & Property Advisory",
                "opt1": "1️⃣ *View Property Listings* — Duplexes, Flats & Land",
                "opt2": "2️⃣ *Book Physical Inspection* — Schedule estate tour",
                "opt3": "3️⃣ *Lease & Title Documents* — Deed of assignment",
                "opt4": "4️⃣ *Talk with Lead Consultant* — Direct consultation"
            },
            "healthcare": {
                "title": "Apex Specialist Clinic & Care",
                "tagline": "24/7 Specialist Medical Services",
                "opt1": "1️⃣ *Book Appointment* — Doctor consultation slot",
                "opt2": "2️⃣ *Prescription Refill* — Order medications",
                "opt3": "3️⃣ *Lab Test Results* — Download diagnostic report",
                "opt4": "4️⃣ *Emergency Care* — Direct doctor line"
            },
            "hospitality": {
                "title": "Grand Imperial Hotel & Resort",
                "tagline": "Luxury Accommodations & Dining",
                "opt1": "1️⃣ *Room Reservations* — Executive suites & rates",
                "opt2": "2️⃣ *Room Service Menu* — Order food to suite",
                "opt3": "3️⃣ *Event Hall Booking* — Conferences & weddings",
                "opt4": "4️⃣ *Concierge Desk* — Speak with front desk"
            },
            "salon": {
                "title": "Queens Beauty Salon & Spa",
                "tagline": "Royal Hair, Nails & Pampering",
                "opt1": "1️⃣ *Hair Styling & Installation* — Wig fixing & braids",
                "opt2": "2️⃣ *Spa & Pedicure* — Royal treatment packages",
                "opt3": "3️⃣ *Book Appointment Slot* — Select date & time",
                "opt4": "4️⃣ *Salon Manager* — Direct booking line"
            },
            "automobile": {
                "title": "Apex Auto Motors & Service",
                "tagline": "Sales, Maintenance & Spare Parts",
                "opt1": "1️⃣ *Vehicle Inventory* — Sedans, SUVs & Trucks",
                "opt2": "2️⃣ *Book Maintenance Service* — Oil change & repair",
                "opt3": "3️⃣ *Order Spare Parts* — Original OEM parts",
                "opt4": "4️⃣ *Speak with Master Mechanic* — Technical support"
            },
            "legal": {
                "title": "Lexis & Partners Legal Practitioners",
                "tagline": "Corporate, Property & Litigation Law",
                "opt1": "1️⃣ *Book Legal Consultation* — Retainer & case review",
                "opt2": "2️⃣ *Document Drafting* — Contracts & agreements",
                "opt3": "3️⃣ *Case Status Update* — Check court filing",
                "opt4": "4️⃣ *Speak with Senior Advocate* — Direct legal line"
            },
            "education": {
                "title": "Global Scholars International Academy",
                "tagline": "Empowering Future Industry Leaders",
                "opt1": "1️⃣ *Course Admissions* — Undergraduate & Diploma",
                "opt2": "2️⃣ *Tuition Fee Structure* — Payment installments",
                "opt3": "3️⃣ *Class Timetable* — Lecture schedules",
                "opt4": "4️⃣ *Admissions Officer* — Direct counseling"
            },
            "restaurant": {
                "title": "Savory Gourmet Restaurant & Lounge",
                "tagline": "Exquisite Intercontinental Dining",
                "opt1": "1️⃣ *Explore Food Menu* — Chef specials & prices",
                "opt2": "2️⃣ *Reserve a Table* — VIP dining slots",
                "opt3": "3️⃣ *Order Takeaway / Delivery* — Instant dispatch",
                "opt4": "4️⃣ *Restaurant Manager* — Event catering"
            },
            "logistics": {
                "title": "Swift Express Cargo & Logistics",
                "tagline": "Fast Nationwide & Global Shipping",
                "opt1": "1️⃣ *Track Cargo Waybill* — Enter tracking ID",
                "opt2": "2️⃣ *Calculate Shipping Quote* — Weight & destination",
                "opt3": "3️⃣ *Book Pickup Service* — Doorstep dispatch",
                "opt4": "4️⃣ *Logistics Dispatcher* — Direct support"
            },
            "retail": {
                "title": biz_name,
                "tagline": "Premium Electronics, Solar & Retail",
                "opt1": "1️⃣ *Product Catalog* — View prices & inventory",
                "opt2": "2️⃣ *Book Physical Inspection* — Schedule store visit",
                "opt3": "3️⃣ *Track Order Shipment* — Delivery status",
                "opt4": "4️⃣ *Store Manager* — Executive client care"
            }
        }

        cfg = niche_configs.get(niche, niche_configs["retail"])
        title = cfg["title"] if niche != "retail" else biz_name

        returning_badge = "\n🌟 *Welcome Back! Resuming your session...*" if is_returning else ""
        last_context = f"\n💡 *Last viewed:* '{last_item}'" if last_item else ""

        return (
            f"🏛️ *[{title} — Client Experience]*\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
            f"{tod_greeting}! {cfg['tagline']}.{returning_badge}\n"
            f"🕒 *Current Local Time:* `{formatted_time}`\n\n"
            f"How may we serve your request today?{last_context}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"{cfg['opt1']}\n"
            f"{cfg['opt2']}\n"
            f"{cfg['opt3']}\n"
            f"{cfg['opt4']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"
            f"💬 Reply 1, 2, 3, or 4 to proceed!"
        )


multi_niche_engine = MultiNicheEngine()
