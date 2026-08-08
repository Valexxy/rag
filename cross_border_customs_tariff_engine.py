class CrossBorderCustomsTariffEngine:
    """Calculates HS Code Customs Duties, Tariff Schedules & Import Clearance Fees for Global Trade."""

    TARIFF_SCHEDULES = {
        "electronics": {"hs_code": "8504.40", "import_duty": 0.20, "levy": 0.05, "handling": 50.0},
        "solar": {"hs_code": "8541.40", "import_duty": 0.05, "levy": 0.00, "handling": 30.0}, # Eco-incentive lower duty
        "clothing": {"hs_code": "6109.10", "import_duty": 0.35, "levy": 0.10, "handling": 40.0},
        "machinery": {"hs_code": "8471.30", "import_duty": 0.10, "levy": 0.02, "handling": 75.0}
    }

    def calculate_import_clearance(self, cif_value: float, category: str = "solar") -> dict:
        """Calculates exact international import duty & customs clearing costs."""
        cat_key = category.lower().strip()
        tariff = self.TARIFF_SCHEDULES.get(cat_key, self.TARIFF_SCHEDULES["electronics"])

        duty_cost = round(cif_value * tariff["import_duty"], 2)
        levy_cost = round(cif_value * tariff["levy"], 2)
        total_customs = round(duty_cost + levy_cost + tariff["handling"], 2)
        landed_cost = round(cif_value + total_customs, 2)

        return {
            "category": cat_key.title(),
            "hs_code": tariff["hs_code"],
            "cif_item_val": cif_value,
            "import_duty": duty_cost,
            "port_levy": levy_cost,
            "terminal_handling": tariff["handling"],
            "total_customs_clearing": total_customs,
            "total_landed_cost": landed_cost
        }

customs_tariff_engine = CrossBorderCustomsTariffEngine()
