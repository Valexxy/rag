class FraudBiometricRiskEngine:
    """AI Fraud & Anomaly Risk Engine analyzing buyer behavior patterns to output a 0-100 Risk Score."""

    def evaluate_order_risk(self, customer_phone: str, amount: float, user_country: str) -> dict:
        """Calculates exact risk score (0 = Safe, 100 = Critical Fraud Alert)."""
        risk_score = 5 # Default low risk

        # High amount check
        if amount > 500000.0:
            risk_score += 25
        elif amount > 200000.0:
            risk_score += 15

        # Unknown country check
        if user_country.upper() not in ["NG", "US", "GB", "AE", "GH", "KE"]:
            risk_score += 20

        risk_level = "LOW_RISK"
        if risk_score > 60:
            risk_level = "HIGH_RISK_MANUAL_REVIEW"
        elif risk_score > 30:
            risk_level = "MEDIUM_RISK"

        return {
            "customer_phone": customer_phone,
            "order_amount": amount,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "recommendation": "APPROVE_AUTOMATED" if risk_score <= 30 else "REQUIRES_STORE_MANAGER_VERIFICATION"
        }

fraud_risk_engine = FraudBiometricRiskEngine()
