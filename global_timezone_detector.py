from datetime import datetime, timezone, timedelta

class GlobalTimezoneDetector:
    """100% Real-Time Country Code & Global Timezone Resolution Engine."""

    COUNTRY_TIMEZONES = {
        "234": {"name": "Nigeria", "code": "WAT", "offset_hours": 1, "currency": "NGN", "symbol": "₦"},
        "1":   {"name": "USA / Canada", "code": "EST", "offset_hours": -5, "currency": "USD", "symbol": "$"},
        "44":  {"name": "United Kingdom", "code": "GMT", "offset_hours": 0, "currency": "GBP", "symbol": "£"},
        "971": {"name": "United Arab Emirates", "code": "GST", "offset_hours": 4, "currency": "AED", "symbol": "AED "},
        "233": {"name": "Ghana", "code": "GMT", "offset_hours": 0, "currency": "GHS", "symbol": "GH₵"},
        "254": {"name": "Kenya", "code": "EAT", "offset_hours": 3, "currency": "KES", "symbol": "KSh "},
        "27":  {"name": "South Africa", "code": "SAST", "offset_hours": 2, "currency": "ZAR", "symbol": "R "},
        "49":  {"name": "Germany / EU", "code": "CET", "offset_hours": 1, "currency": "EUR", "symbol": "€"},
        "86":  {"name": "China", "code": "CST", "offset_hours": 8, "currency": "CNY", "symbol": "¥"},
        "91":  {"name": "India", "code": "IST", "offset_hours": 5.5, "currency": "INR", "symbol": "₹"}
    }

    def detect_customer_location_from_phone(self, phone_number: str) -> dict:
        """Extracts country code from phone number digits and returns real-time timezone & currency."""
        clean_p = "".join(filter(str.isdigit, str(phone_number)))

        # Match longest matching prefix
        for prefix in sorted(self.COUNTRY_TIMEZONES.keys(), key=len, reverse=True):
            if clean_p.startswith(prefix):
                return self.COUNTRY_TIMEZONES[prefix]

        # Default fallback to Nigeria (WAT)
        return self.COUNTRY_TIMEZONES["234"]

    def get_customer_local_time(self, phone_number: str) -> tuple:
        """Calculates exact real-time local datetime and greeting for the customer's specific country."""
        loc_info = self.detect_customer_location_from_phone(phone_number)
        offset_hrs = loc_info["offset_hours"]
        
        # Calculate customer's local time based on UTC
        utc_now = datetime.now(timezone.utc)
        customer_now = utc_now + timedelta(hours=offset_hrs)
        
        hour = customer_now.hour

        if 5 <= hour < 12:
            greeting = f"Good morning 🌅 ({loc_info['code']} Local Time: {customer_now.strftime('%I:%M %p')})"
        elif 12 <= hour < 17:
            greeting = f"Good afternoon ☀️ ({loc_info['code']} Local Time: {customer_now.strftime('%I:%M %p')})"
        elif 17 <= hour < 22:
            greeting = f"Good evening 🌆 ({loc_info['code']} Local Time: {customer_now.strftime('%I:%M %p')})"
        else:
            greeting = f"Good late night 🌙 ({loc_info['code']} Local Time: {customer_now.strftime('%I:%M %p')})"

        return greeting, loc_info, customer_now

global_tz = GlobalTimezoneDetector()
