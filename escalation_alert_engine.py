import time
from evolution_interactive import send_whatsapp_message

class EscalationAlertEngine:
    """High-Priority Multi-Stage Escalation Engine to ensure managers respond in minutes."""

    def __init__(self):
        self.active_handovers = {} # Key: customer_phone -> handover_meta

    def register_human_handover(self, instance_name: str, owner_phone: str, customer_phone: str, reason: str, details: str):
        """Registers a human handover and schedules high-priority escalation tracking."""
        clean_cust = "".join(filter(str.isdigit, str(customer_phone)))
        clean_owner = "".join(filter(str.isdigit, str(owner_phone)))

        self.active_handovers[clean_cust] = {
            "instance_name": instance_name,
            "owner_phone": clean_owner,
            "customer_phone": clean_cust,
            "reason": reason,
            "details": details,
            "handover_time": time.time(),
            "alerts_sent": 1
        }

    def resolve_handover(self, customer_phone: str):
        """Resolves handover when human agent sends a message."""
        clean_cust = "".join(filter(str.isdigit, str(customer_phone)))
        if clean_cust in self.active_handovers:
            del self.active_handovers[clean_cust]

    def trigger_escalation_pings(self):
        """Background checker: Sends high-priority follow-up pings if manager hasn't responded."""
        now = time.time()
        for cust_phone, meta in list(self.active_handovers.items()):
            elapsed_mins = (now - meta["handover_time"]) / 60.0

            # T+3 Minutes: High Priority Follow-Up Ping #2
            if 3.0 <= elapsed_mins < 7.0 and meta["alerts_sent"] < 2:
                meta["alerts_sent"] = 2
                ping_msg = f"""🔔 *[URGENT FOLLOW-UP - 3 MINS ELAPSED]*
---------------------------------------------
📱 *Customer:* `+{cust_phone}` is waiting for your reply!
⚡ *Reason:* {meta['reason']}

💬 Reply to customer now or click: https://wa.me/{cust_phone}"""
                send_whatsapp_message(meta["instance_name"], meta["owner_phone"], ping_msg)

            # T+7 Minutes: High Priority Emergency Escalation #3
            elif elapsed_mins >= 7.0 and meta["alerts_sent"] < 3:
                meta["alerts_sent"] = 3
                emergency_msg = f"""🚨🚨 *[CRITICAL ALERT - 7 MINS NO RESPONSE]*
---------------------------------------------
⚠️ Customer `+{cust_phone}` has been waiting for 7 minutes!
👉 Please reply immediately to prevent customer loss: https://wa.me/{cust_phone}"""
                send_whatsapp_message(meta["instance_name"], meta["owner_phone"], emergency_msg)

escalation_alert_engine = EscalationAlertEngine()
