class SovereignDirectoryEngine:
    """Premium Verified Customer & Merchant Directory / Customer Finder Engine."""

    VERIFIED_DIRECTORY_LISTINGS = [
        {
            "id": "dir-01",
            "name": "Teeslux Electronics & Solar Hub",
            "category": "solar",
            "city": "Onitsha",
            "phone": "2348072015725",
            "rating": "5.0 ⭐ (Verified)",
            "top_item": "30,000mAh Solar Power Bank & Inverters",
            "price_sample": "₦25,000.00"
        },
        {
            "id": "dir-02",
            "name": "Alaba Tech Wholesale Direct",
            "category": "tech",
            "city": "Lagos",
            "phone": "2348123456789",
            "rating": "4.9 ⭐ (Verified)",
            "top_item": "Smartphones & Laptop Accessories",
            "price_sample": "₦15,000.00"
        },
        {
            "id": "dir-03",
            "name": "Ariaria Leather & Shoe Factory",
            "category": "fashion",
            "city": "Aba",
            "phone": "2348033334444",
            "rating": "4.8 ⭐ (Verified)",
            "top_item": "Pure Leather Boots & Men's Shoes",
            "price_sample": "₦18,500.00"
        }
    ]

    def search_directory(self, category_or_city: str) -> str:
        """Finds verified stores, items, and direct 1-tap buyer-seller contact links."""
        q = category_or_city.lower().strip()
        matches = []

        for item in self.VERIFIED_DIRECTORY_LISTINGS:
            if q in item["category"].lower() or q in item["city"].lower() or q in item["name"].lower():
                matches.append(item)

        if not matches:
            matches = self.VERIFIED_DIRECTORY_LISTINGS[:2]

        lines = []
        for m in matches:
            lines.append(f"""🏢 *{m['name']}*
📍 *City:* {m['city']} | 🏆 *Rating:* {m['rating']}
📦 *Featured:* {m['top_item']} ({m['price_sample']})
📲 *Direct Chat:* https://wa.me/{m['phone']}""")

        return f"""🔍 *[PREMIUM SOVEREIGN MERCHANT DIRECTORY]*
---------------------------------------------
Found top verified supplier matches for: `{category_or_city}`

{chr(10).join(lines)}

---------------------------------------------
👉 *List Your Store:* Type `#list-store <name> | <category> | <city>` to get featured in our global directory & receive new customer leads daily!"""

sovereign_directory = SovereignDirectoryEngine()
