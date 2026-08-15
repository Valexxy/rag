"""
====================================================================
HUMAN COMMAND PROCESSOR v2026
====================================================================
Parses WhatsApp shortcut commands sent by the Store Manager and
dispatches appropriate actions:
  #approve  [ORDER_REF]              — Verify payment & authorize dispatch
  #dispatch [ORDER_REF] [Rider Info] — Send live rider info to customer
  #quote    [ORDER_REF] [AMOUNT]     — Send custom price to buyer
  #mute     [CUSTOMER_PHONE]         — Mute AI for that customer
  #unmute   [CUSTOMER_PHONE]         — Re-enable AI for that customer
  #refund   [ORDER_REF]              — Flag order for refund processing
  #credit   [CUSTOMER_PHONE]         — Show store credit balance
====================================================================
"""

import re
import logging

logger = logging.getLogger("HumanCommandProcessor")


class HumanCommandProcessor:

    def parse(self, message_text: str, manager_phone: str, tenant: dict) -> dict | None:
        """
        Parses a message from the Store Manager and returns a command action dict.
        Returns None if the message is not a recognized command.
        """
        text = message_text.strip()
        if not text.startswith("#"):
            return None

        parts = text.split(maxsplit=2)
        cmd = parts[0].lower()

        # ── #approve [ORDER_REF] ─────────────────────────────────────────
        if cmd == "#approve" and len(parts) >= 2:
            order_ref = parts[1].upper()
            return {
                "action": "APPROVE_ORDER",
                "order_ref": order_ref,
                "customer_message": (
                    f"🎉 *[Order Verified & Dispatch Authorized!]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Your payment for Order *#{order_ref}* has been personally verified by our Store Manager!\n\n"
                    f"📦 Your goods are now packed and queued for waybill dispatch.\n"
                    f"🚚 You will receive your rider's details and tracking info shortly!\n\n"
                    f"Thank you for shopping with *{tenant.get('business_name', 'our store')}*! 🙏"
                ),
                "db_status": "PAID_APPROVED"
            }

        # ── #dispatch [ORDER_REF] [Rider info] ──────────────────────────
        if cmd == "#dispatch" and len(parts) >= 3:
            import random
            order_ref = parts[1].upper()
            rider_info = parts[2]
            otp_code = f"{random.randint(1000, 9999)}"

            return {
                "action": "DISPATCH_ORDER",
                "order_ref": order_ref,
                "otp_code": otp_code,
                "customer_message": (
                    f"🚚 *[Your Order Is On Its Way!]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Order *#{order_ref}* has been dispatched!\n\n"
                    f"🏍️ *Delivery Agent:* {rider_info}\n"
                    f"🔐 *Secret Delivery OTP:* `{otp_code}`\n\n"
                    f"⚠️ *Mandatory Security:* Provide this 4-digit secret OTP to the rider upon receiving your package to verify delivery!\n\n"
                    f"📞 For any delivery issues, contact our manager: +{tenant.get('owner_phone', manager_phone)}"
                ),
                "db_status": "DISPATCHED"
            }

        # ── #verifyotp [ORDER_REF] [OTP_CODE] ────────────────────────────
        if cmd == "#verifyotp" and len(parts) >= 3:
            order_ref = parts[1].upper()
            otp_input = parts[2].strip()
            return {
                "action": "VERIFY_POD_OTP",
                "order_ref": order_ref,
                "user_otp": otp_input,
                "manager_ack": f"🔍 Verifying Delivery OTP '{otp_input}' for Order #{order_ref}..."
            }


        # ── #quote [ORDER_REF] [AMOUNT] ──────────────────────────────────
        if cmd == "#quote" and len(parts) >= 3:
            order_ref = parts[1].upper()
            amount = parts[2]
            return {
                "action": "SEND_QUOTE",
                "order_ref": order_ref,
                "customer_message": (
                    f"💰 *[Custom Price Quote — Order #{order_ref}]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Our Store Manager has confirmed the following special price for your request:\n\n"
                    f"💵 *Price:* ₦{amount}\n\n"
                    f"Reply *#buy* to proceed with payment, or ask any questions!"
                )
            }

        # ── #mute [CUSTOMER_PHONE] ────────────────────────────────────────
        if cmd == "#mute" and len(parts) >= 2:
            phone = parts[1]
            return {
                "action": "MUTE_AI",
                "customer_phone": phone,
                "manager_ack": f"✅ AI muted for {phone}. You are now in full control of that conversation."
            }

        # ── #unmute [CUSTOMER_PHONE] ──────────────────────────────────────
        if cmd == "#unmute" and len(parts) >= 2:
            phone = parts[1]
            return {
                "action": "UNMUTE_AI",
                "customer_phone": phone,
                "manager_ack": f"✅ AI re-enabled for {phone}."
            }

        # ── #refund [ORDER_REF] ───────────────────────────────────────────
        if cmd == "#refund" and len(parts) >= 2:
            order_ref = parts[1].upper()
            return {
                "action": "FLAG_REFUND",
                "order_ref": order_ref,
                "customer_message": (
                    f"💸 *[Refund Initiated — Order #{order_ref}]*\n"
                    f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
                    f"Our Store Manager has initiated a refund for your Order *#{order_ref}*.\n\n"
                    f"⏳ Refund will be processed to your original bank account within 24 hours.\n"
                    f"📞 For any inquiries: +{tenant.get('owner_phone', manager_phone)}"
                ),
                "db_status": "refunded"
            }

        # ── #credit [CUSTOMER_PHONE] ──────────────────────────────────────
        if cmd == "#credit" and len(parts) >= 2:
            phone = parts[1]
            return {
                "action": "CHECK_CREDIT",
                "customer_phone": phone
            }

        logger.warning(f"[HumanCommandProcessor] Unrecognized command: {text}")
        return None


human_command_processor = HumanCommandProcessor()
