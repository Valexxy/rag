class GamificationRetentionEngine:
    """Trader Retention, Daily Streaks & Merchant Badge System."""

    @staticmethod
    def get_merchant_tier(transaction_count: int, revenue_total: float) -> tuple:
        """Calculates gamified merchant level badge."""
        if revenue_total >= 5000000 or transaction_count >= 100:
            return "💎 Sovereign Diamond Merchant", "VIP 0.5% Transaction Fee Discount"
        elif revenue_total >= 1000000 or transaction_count >= 30:
            return "🥇 Gold Elite Merchant", "Priority Logistics Dispatch"
        elif revenue_total >= 250000 or transaction_count >= 10:
            return "🥈 Silver Merchant", "Verified SaaS Trust Badge"
        return "🥉 Bronze Rising Merchant", "Standard Free Tier"

    @staticmethod
    def format_daily_streak_card(merchant_phone: str, streak_days: int = 7, revenue_today: float = 48500.0) -> str:
        """Renders addictive gamified streak report for merchants."""
        tier_name, perk = GamificationRetentionEngine.get_merchant_tier(streak_days * 3, revenue_today * 7)

        return f"""🔥 *[MERCHANT DAILY STREAK: {streak_days} DAYS IN A ROW!]*
---------------------------------------------
📱 *Merchant:* `{merchant_phone}`
🏆 *Rank:* {tier_name}
🎁 *Active Perk:* _{perk}_
📈 *Profit Score Today:* +18.4% growth

Keep selling daily to maintain your streak and unlock Diamond SaaS rewards!"""

gamification_engine = GamificationRetentionEngine()
