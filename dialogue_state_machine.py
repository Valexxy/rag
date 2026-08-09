"""
====================================================================
PERSISTED DIALOGUE STATE MACHINE & CHATWOOT MUTING ENGINE (v2030)
====================================================================
Manages real-time conversation state per customer remoteJid:

States:
1. IDLE: Default listening state.
2. DISAMBIGUATING: Presented numbered options (1️⃣, 2️⃣, 3️⃣), awaiting numeric choice.
3. ITEM_INSPECTING: Customer viewing product card, awaiting #buy or #human.
4. ORDER_PENDING: Customer clicked #buy, awaiting payment transfer receipt.
5. HUMAN_ESCALATED: Chat transferred to Store Manager. Bot is MUTED for this customer until #resolve.

Commands:
- #reply <phone> | <message>: Manager sends direct message to customer.
- #resolve <phone>: Manager marks conversation resolved. Un-mutes bot.
- #mute <phone>: Manager manually mutes bot for a customer.
"""

import time
import logging
from typing import Dict, Any, Tuple

logger = logging.getLogger(__name__)


class DialogueStateMachine:
    """Zero-Downtime Session State & Chatwoot Muting Engine."""

    def __init__(self):
        # Maps remoteJid -> session dict
        # session = {"state": "IDLE", "updated_at": timestamp, "slots": {}}
        self._sessions: Dict[str, Dict[str, Any]] = {}

    def get_session(self, remote_jid: str) -> Dict[str, Any]:
        clean_jid = str(remote_jid).strip().lower()
        if clean_jid not in self._sessions:
            self._sessions[clean_jid] = {
                "state": "IDLE",
                "updated_at": time.time(),
                "slots": {}
            }
        return self._sessions[clean_jid]

    def set_state(self, remote_jid: str, state: str, slots: Dict[str, Any] = None):
        session = self.get_session(remote_jid)
        session["state"] = state
        session["updated_at"] = time.time()
        if slots:
            session["slots"].update(slots)
        logger.info(f"[State Machine] JID '{remote_jid}' -> State: '{state}'")

    def is_bot_muted(self, remote_jid: str) -> bool:
        session = self.get_session(remote_jid)
        return session.get("state") == "HUMAN_ESCALATED"

    def handle_manager_command(self, text: str, sender_phone: str) -> Tuple[bool, str]:
        """
        Parses manager admin commands:
        - #reply <phone> | <message>
        - #resolve <phone>
        - #mute <phone>
        """
        raw = text.strip()

        # #reply <phone> | <message>
        if raw.startswith("#reply"):
            parts = raw[6:].strip().split("|", 1)
            if len(parts) == 2:
                target_phone = "".join(filter(str.isdigit, parts[0]))
                reply_msg = parts[1].strip()
                return True, f"REPLY_CMD:{target_phone}:{reply_msg}"

        # #resolve <phone>
        if raw.startswith("#resolve"):
            target_phone = "".join(filter(str.isdigit, raw[8:]))
            if target_phone:
                self.set_state(f"{target_phone}@s.whatsapp.net", "IDLE")
                return True, f"RESOLVE_CMD:{target_phone}"

        # #mute <phone>
        if raw.startswith("#mute"):
            target_phone = "".join(filter(str.isdigit, raw[5:]))
            if target_phone:
                self.set_state(f"{target_phone}@s.whatsapp.net", "HUMAN_ESCALATED")
                return True, f"MUTE_CMD:{target_phone}"

        return False, ""


state_machine = DialogueStateMachine()
