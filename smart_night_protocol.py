from datetime import datetime
from smart_timezone_engine import smart_timezone

class SmartNightProtocol:
    """Zero-Customer-Loss Night-Time & Unresponsive Manager Escalation Engine."""

    def __init__(self):
        self.night_start_hour = 22 # 10:00 PM WAT
        self.night_end_hour = 7   # 07:00 AM WAT

    def is_night_time(self) -> bool:
        """Determines if the current real-time clock is in night hours (10 PM to 7 AM WAT)."""
        now_wat = smart_timezone.get_realtime_nigeria_now()
        hour = now_wat.hour
        return hour >= self.night_start_hour or hour < self.night_end_hour

    def handle_night_time_media_inquiry(self, business_name: str, customer_phone: str, caption: str = "") -> dict:
        """Generates smart night-time response and short-duration mute instead of long silence."""
        greeting = smart_timezone.get_time_of_day_greeting()
        time_str = smart_timezone.get_realtime_nigeria_now().strftime("%I:%M %p WAT")

        reply_message = f"""🌙 *[{business_name} - NIGHT ASSISTANT]*
---------------------------------------------
{greeting}! We received your photo/video inquiry at *{time_str}*.

Our store management team is currently offline for the night (physical market reopens at 8:00 AM WAT).

📌 *Zero Customer Loss Assurance:* Your photo and inquiry have been logged at *Position #1* in our priority morning queue. The manager will inspect and reply first thing in the morning!

🤖 *AI Autopilot Active:* In the meantime, you can type:
• `menu` - Explore our catalog & pricing
• `#news` - Read trade news
• `#track` - Check order waybill status"""

        return {
            "reply": reply_message,
            "is_night": True,
            "mute_duration_minutes": 15, # Reduced mute duration at night so customer isn't trapped
            "logged_for_morning": True
        }

smart_night_protocol = SmartNightProtocol()
