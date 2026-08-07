class LoyaltyRewardsEngine:
    """Manages customer loyalty points, cashback balance, and promo coupons."""

    @staticmethod
    def calculate_earned_points(amount: float) -> int:
        """Earn 1 point per NGN 100 spent."""
        return int(amount // 100)

    @staticmethod
    def format_loyalty_summary(customer_phone: str, points: int = 150) -> str:
        """Formats clean loyalty balance report for WhatsApp client."""
        return f"""🪙 *[LOYALTY & CASHBACK REWARDS]*
---------------------------------------------
📱 *Customer:* `{customer_phone}`
🪙 *Loyalty Balance:* *{points} Points*
🎁 *Available Voucher:* Use code `SAVE10` for 10% off your next purchase!"""

loyalty_engine = LoyaltyRewardsEngine()
