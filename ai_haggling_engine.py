class AIHagglingEngine:
    """World-First AI Dynamic Haggling & Margin-Aware Bargaining Engine for Informal Markets."""

    @staticmethod
    def negotiate_price(list_price: float, floor_price: float, customer_offer: float, currency_symbol: str = "₦") -> dict:
        """Evaluates customer's bargain offer against merchant's minimum floor price."""
        if customer_offer >= list_price:
            return {
                "status": "ACCEPTED",
                "agreed_price": list_price,
                "reply": f"🤝 *[DEAL ACCEPTED]*\n\nYour offer of *{currency_symbol}{customer_offer:,.2f}* is accepted! You can proceed to payment."
            }

        if customer_offer >= floor_price:
            return {
                "status": "ACCEPTED_DISCOUNT",
                "agreed_price": customer_offer,
                "reply": f"🤝 *[BARGAIN ACCEPTED]*\n\nDeal! I can give it to you at your offered price of *{currency_symbol}{customer_offer:,.2f}*. Let's complete your order!"
            }

        # If customer offer is below floor price -> Counter-offer at midpoint
        counter_offer = round((floor_price + list_price) / 2.0, 2)
        if customer_offer < floor_price * 0.7:
            # Lowball offer
            return {
                "status": "REJECTED_LOWBALL",
                "counter_price": floor_price,
                "reply": f"💬 *[PRICE COUNTER-OFFER]*\n\nAh, my friend! *{currency_symbol}{customer_offer:,.2f}* is too low for this quality item! The lowest I can do to help you today is *{currency_symbol}{floor_price:,.2f}*. Shall I book it for you?"
            }
        else:
            return {
                "status": "COUNTER_OFFER",
                "counter_price": counter_offer,
                "reply": f"💬 *[SPECIAL DISCOUNTER COUNTER-OFFER]*\n\nI can't do *{currency_symbol}{customer_offer:,.2f}*, but because we value your business, I can give it to you for *{currency_symbol}{counter_offer:,.2f}* final price! Deal?"
            }

ai_haggling = AIHagglingEngine()
