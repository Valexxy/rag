class OmnichannelSync:
    """Omnichannel Message Router: Syncs Web Chat, Telegram, Instagram DMs into WhatsApp Core."""

    @staticmethod
    def normalize_inbound_payload(channel: str, raw_payload: dict) -> dict:
        """Normalizes external channel message into unified WhatsApp schema."""
        if channel == "telegram":
            msg = raw_payload.get("message", {})
            sender = str(msg.get("from", {}).get("id", ""))
            text = msg.get("text", "")
            return {"channel": "telegram", "sender_id": sender, "text": text}

        elif channel == "web_chat":
            return {
                "channel": "web_chat",
                "sender_id": raw_payload.get("client_id", "web_guest"),
                "text": raw_payload.get("message", "")
            }

        return {"channel": "whatsapp", "sender_id": raw_payload.get("phone", ""), "text": raw_payload.get("text", "")}

omnichannel_sync = OmnichannelSync()
