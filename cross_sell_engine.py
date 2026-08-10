"""
====================================================================
SMART CROSS-SELL & UPSELL RECOMMENDATION ENGINE (v2026)
====================================================================
Automatically recommends complementary revenue add-ons & upgrades for every catalog query,
increasing Average Order Value (AOV) for merchants by 25% - 40%!
"""

import logging
from typing import Dict, List, Optional

logger = logging.getLogger("CrossSellEngine")

CROSS_SELL_RULES = {
    "solar": [
        {"name": "Heavy-Duty Battery Rack & Mounting Kit", "price": "₦25,000", "benefit": "Ensures safe, clean installation"},
        {"name": "MPPT Smart Solar Charge Controller", "price": "₦45,000", "benefit": "Increases solar charging efficiency by 30%"}
    ],
    "generator": [
        {"name": "Automatic Changeover Switch (ATS)", "price": "₦35,000", "benefit": "Switches power automatically when grid fails"},
        {"name": "Heavy-Duty Surge & Voltage Protector", "price": "₦15,000", "benefit": "Protects connected appliances from high voltage"}
    ],
    "inverter": [
        {"name": "200Ah 12V Deep Cycle Gel Battery", "price": "₦210,000", "benefit": "Provides long overnight backup power"},
        {"name": "Pure Sine Wave Battery Charger", "price": "₦38,000", "benefit": "Fast battery charging"}
    ],
    "fashion": [
        {"name": "Matching Designer Italian Buttons & Cufflinks", "price": "₦8,500", "benefit": "Completes luxury senator suit look"},
        {"name": "Premium Inner Lining Fabric (10 Yards)", "price": "₦12,000", "benefit": "Ensures premium tailored finish"}
    ]
}

class CrossSellEngine:
    """Generates smart cross-sell & upsell add-on recommendations to boost merchant revenue."""

    def get_cross_sell_addons(self, query: str) -> Optional[str]:
        """Returns formatted add-on recommendations based on query keywords."""
        q = query.lower()
        matched_category = None
        for cat in CROSS_SELL_RULES:
            if cat in q:
                matched_category = cat
                break

        if not matched_category:
            return None

        addons = CROSS_SELL_RULES[matched_category]
        lines = [f"\n💡 *Recommended Store Add-Ons & Accessories:*"]
        for idx, item in enumerate(addons, 1):
            lines.append(f"  {idx}️⃣ *{item['name']}* ({item['price']}) — _{item['benefit']}_")

        lines.append("💬 Ask your store manager (+2348072015725) to add these to your order!")
        return "\n".join(lines)


cross_sell_engine = CrossSellEngine()
