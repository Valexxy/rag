import os
from datetime import datetime, timedelta, timezone
from supabase import create_client
from dotenv import load_dotenv

load_dotenv()

# Check for either SUPABASE_KEY or SUPABASE_SERVICE_ROLE_KEY
supabase_key = os.environ.get("SUPABASE_KEY") or os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
supabase_url = os.environ.get("SUPABASE_URL")

supabase = create_client(supabase_url, supabase_key)

def is_bot_muted(phone_number: str) -> bool:
    """Checks if the bot is currently locked out for a specific customer."""
    res = supabase.table("bot_mutes").select("muted_until").eq("customer_phone", phone_number).execute()
    if res.data:
        muted_until = datetime.fromisoformat(res.data[0]["muted_until"])
        return datetime.now(timezone.utc) < muted_until
    return False

def mute_bot_for_owner(phone_number: str, minutes: int = 60):
    """Locks the bot for X minutes when the owner types manually on WhatsApp."""
    mute_until = (datetime.now(timezone.utc) + timedelta(minutes=minutes)).isoformat()
    supabase.table("bot_mutes").upsert({"customer_phone": phone_number, "muted_until": mute_until}).execute()