from datetime import datetime, timezone, timedelta

class SmartTimezoneEngine:
    """100% Real-Time Smart Timezone & Time-of-Day Context Engine."""

    def __init__(self):
        # Default UTC+1 offset for West Africa Time (WAT / Nigeria)
        self.wat_offset = timedelta(hours=1)

    def get_realtime_nigeria_now(self) -> datetime:
        """Returns exact real-time WAT (Africa/Lagos) timestamp."""
        return datetime.now(timezone.utc) + self.wat_offset

    def get_time_of_day_greeting(self) -> str:
        """Generates dynamic time-of-day greetings based on real-time WAT clock."""
        now = self.get_realtime_nigeria_now()
        hour = now.hour

        if 5 <= hour < 12:
            return "Good morning 🌅"
        elif 12 <= hour < 17:
            return "Good afternoon ☀️"
        elif 17 <= hour < 22:
            return "Good evening 🌆"
        else:
            return "Good late night 🌙"

    def get_business_hours_status(self, open_hour: int = 8, close_hour: int = 18) -> dict:
        """Computes real-time physical store operating status."""
        now = self.get_realtime_nigeria_now()
        hour = now.hour

        is_open = open_hour <= hour < close_hour
        time_str = now.strftime("%I:%M %p WAT")

        if is_open:
            status_text = "🟢 *STORE OPEN:* Physical market & dispatch teams are active."
        else:
            status_text = "🌙 *STORE CLOSED:* Physical market is closed for the day, but our AI autopilot is taking orders & logging inquiries 24/7!"

        return {
            "is_open": is_open,
            "current_time_str": time_str,
            "greeting": self.get_time_of_day_greeting(),
            "status_text": status_text
        }

smart_timezone = SmartTimezoneEngine()
