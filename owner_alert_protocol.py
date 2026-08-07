from evolution_interactive import send_whatsapp_message

class OwnerAlertProtocol:
    """Urgent Push Alert Protocol for High-Value Leads & Human Handoffs."""

    @staticmethod
    def send_urgent_owner_alert(instance_name: str, owner_phone: str, customer_phone: str, reason: str, details: str = ""):
        """Sends immediate high-priority push notification to business owner on WhatsApp."""
        if not owner_phone:
            return

        alert_message = f"""🚨 *[URGENT MANAGER ACTION REQUIRED]*
---------------------------------------------
📱 *Customer Phone:* `{customer_phone}`
⚡ *Reason:* {reason}
📝 *Details:* _{details}_

👉 *Quick Actions:*
Reply to customer in chat to auto-mute bot, or type:
• `#unmute {customer_phone}` - Resume AI
• `#add` - Add item to catalog"""

        send_whatsapp_message(instance_name, owner_phone, alert_message)

owner_alert = OwnerAlertProtocol()
