"""
====================================================================
META WHATSAPP SENDER v2026
====================================================================
Sends all outbound WhatsApp messages via Meta Cloud API:
- Plain text messages
- Native product image cards with price + Buy button
- Human verification & manager alert cards
====================================================================
"""

import os
import json
import logging
import urllib.request
import urllib.error

logger = logging.getLogger("MetaWhatsAppSender")

META_PHONE_ID = os.environ.get("META_PHONE_NUMBER_ID", "1242614362274985")
META_TOKEN = os.environ.get("META_PERMANENT_TOKEN", "")
META_API_URL = f"https://graph.facebook.com/v20.0/{META_PHONE_ID}/messages"


def _send(payload: dict) -> bool:
    if not META_TOKEN:
        logger.warning("[MetaSender] No META_PERMANENT_TOKEN set — skipping send")
        return False
    headers = {
        "Authorization": f"Bearer {META_TOKEN}",
        "Content-Type": "application/json"
    }
    req = urllib.request.Request(
        META_API_URL,
        data=json.dumps(payload).encode(),
        headers=headers,
        method="POST"
    )
    try:
        with urllib.request.urlopen(req, timeout=8) as r:
            result = json.loads(r.read().decode())
            msg_id = result.get("messages", [{}])[0].get("id", "?")
            logger.info(f"[MetaSender] ✅ Sent: {msg_id}")
            return True
    except urllib.error.HTTPError as e:
        logger.error(f"[MetaSender] HTTP {e.code}: {e.read().decode()}")
        return False
    except Exception as e:
        logger.error(f"[MetaSender] Error: {e}")
        return False


def send_whatsapp_text(to: str, text: str) -> bool:
    """Send a plain text WhatsApp message."""
    phone = to.replace("+", "").replace(" ", "")
    payload = {
        "messaging_product": "whatsapp",
        "recipient_type": "individual",
        "to": phone,
        "type": "text",
        "text": {"preview_url": False, "body": text}
    }
    return _send(payload)


def send_product_image_card(
    to: str,
    product_name: str,
    price: float,
    description: str,
    image_url: str,
    order_ref: str
) -> bool:
    """
    Sends a native Meta WhatsApp image message with product photo,
    price badge, description, and Buy Now CTA button.
    """
    phone = to.replace("+", "").replace(" ", "")
    caption = (
        f"🛍️ *{product_name}*\n"
        f"💰 *Price:* ₦{price:,.2f}\n"
        f"📦 {description}\n\n"
        f"Reply *#buy* or send *Order #{order_ref}* to purchase!"
    )
    if image_url:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": caption
            }
        }
    else:
        payload = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": phone,
            "type": "text",
            "text": {"preview_url": False, "body": caption}
        }
    return _send(payload)


def send_catalog_gallery(to: str, products: list, business_name: str) -> bool:
    """
    Sends a visual product gallery — one image card per product.
    If no images are set, sends a formatted text list.
    """
    phone = to.replace("+", "").replace(" ", "")

    has_images = any(p.get("image_url") for p in products[:5])

    if not has_images:
        lines = [f"🛒 *{business_name} — Product Catalog*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n"]
        for i, p in enumerate(products[:10], 1):
            lines.append(f"{i}️⃣ *{p['name']}* — ₦{float(p['price']):,.2f}")
        lines.append("\nReply with a product name or number to get more details & place an order!")
        return send_whatsapp_text(to, "\n".join(lines))

    # Send image cards for up to 5 products
    success = True
    for p in products[:5]:
        ok = send_product_image_card(
            to=to,
            product_name=p["name"],
            price=float(p["price"]),
            description=p.get("description", ""),
            image_url=p.get("image_url", ""),
            order_ref=str(p.get("id", ""))
        )
        success = success and ok
    return success


def send_manager_alert(manager_phone: str, message: str) -> bool:
    """Sends an urgent alert directly to the Store Manager's WhatsApp."""
    return send_whatsapp_text(f"+{manager_phone}", message)
