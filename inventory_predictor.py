class InventoryPredictor:
    """Predicts stock depletion and generates restock alerts."""

    @staticmethod
    def check_stock_level(item_name: str, current_stock: int, min_threshold: int = 5) -> str:
        """Returns stock alert notification if below threshold."""
        if current_stock <= min_threshold:
            return f"⚠️ *[INVENTORY RESTOCK ALERT]*\n\nItem `*{item_name}*` is down to *{current_stock}* unit(s) remaining. Reorder recommended immediately to prevent lost sales."
        return ""

inventory_predictor = InventoryPredictor()
