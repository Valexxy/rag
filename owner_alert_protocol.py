from evolution_interactive import send_whatsapp_message

class OwnerAlertProtocol:
    """Flexible Push Alert Protocol for High-Value Leads, Direct Conversations & Management Actions."""

    @staticmethod
    def send_urgent_owner_alert(instance_name: str, owner_phone: str, customer_phone: str, reason: str, details: str = "") -> str:
        """Sends immediate high-priority push notification to business owner on WhatsApp with flexible 1-tap options."""
        if not owner_phone:
            return ""

        clean_c_phone = "".join(filter(str.isdigit, str(customer_phone)))

        alert_message = f"""🚨 *[MANAGER ACTION REQUIRED - HIGH PRIORITY]*
---------------------------------------------
📱 *Customer Phone:* `+{clean_c_phone}`
⚡ *Reason:* {reason}
📝 *Details:* _{details}_

💬 *Direct Chat Link:* https://wa.me/{clean_c_phone}?text=Hello%20from%20management!

---------------------------------------------
👉 *Quick 1-Tap Phone Commands (Reply to this chat):*
• `#reply {clean_c_phone} | Your message` (Send message via bot)
• `#discount {clean_c_phone} | 10%` (Give custom discount)
• `#unmute {clean_c_phone}` (Resume AI autopilot)
• `#add Item | Price | Specs` (Add new stock)"""

        send_whatsapp_message(instance_name, owner_phone, alert_message)
        return alert_message

owner_alert = OwnerAlertProtocol()
