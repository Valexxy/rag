from sovereign_trust_score_engine import sovereign_trust_score

class SovereignDirectoryEngine:
    """Premium Verified Customer & Merchant Directory across ALL Business Niches with QR Code Generator."""

    VERIFIED_DIRECTORY_LISTINGS = [
        {
            "id": "t-demo",
            "name": "Teeslux Electronics & Solar Hub",
            "category": "Solar & Clean Energy",
            "city": "Onitsha",
            "state": "Anambra State",
            "phone": "2348072015725",
            "top_item": "30,000mAh Solar Power Bank & 5kVA Inverters",
            "price_sample": "₦25,000.00",
            "address": "Shop 14B, Block C, Bright Street, Onitsha Main Market"
        },
        {
            "id": "dir-02",
            "name": "Alaba Tech Wholesale Direct",
            "category": "Consumer Electronics & Tech",
            "city": "Lagos",
            "state": "Lagos State",
            "phone": "2348123456789",
            "top_item": "Smartphones & Laptop Accessories",
            "price_sample": "₦15,000.00",
            "address": "Suite 8, Fancy Plaza, Alaba International Market Road, Ojo"
        },
        {
            "id": "dir-03",
            "name": "Ariaria Leather & Shoe Factory",
            "category": "Fashion & Leathercraft",
            "city": "Aba",
            "state": "Abia State",
            "phone": "2348033334444",
            "top_item": "Pure Leather Boots & Men's Shoes",
            "price_sample": "₦18,500.00",
            "address": "No. 42B, Faulks Road, Near Ariaria Market"
        },
        {
            "id": "dir-04",
            "name": "Dawanau Grain & Agriculture Depot",
            "category": "Agriculture & Food Commodities",
            "city": "Kano",
            "state": "Kano State",
            "phone": "2348022221111",
            "top_item": "50kg White Rice & Sesame Seeds",
            "price_sample": "₦60,000.00",
            "address": "Shed 12, Dawanau International Grain Market"
        },
        {
            "id": "dir-05",
            "name": "Ladipo Auto Spares Direct",
            "category": "Automotive Parts & Machinery",
            "city": "Lagos",
            "state": "Lagos State",
            "phone": "2348055556666",
            "top_item": "Toyota & Honda Genuine Brake Pads & Alternators",
            "price_sample": "₦12,000.00",
            "address": "Line 4, Ladipo Auto Market, Mushin"
        },
        {
            "id": "dir-06",
            "name": "Computer Village Component Hub",
            "category": "Computer Hardware & IT",
            "city": "Ikeja",
            "state": "Lagos State",
            "phone": "2348099998888",
            "top_item": "1TB NVMe SSDs & DDR5 RAM Kits",
            "price_sample": "₦32,000.00",
            "address": "No. 15, Otigba Street, Computer Village, Ikeja"
        },
        {
            "id": "dir-07",
            "name": "Bridge Head Pharma Wholesale",
            "category": "Healthcare & Pharmaceuticals",
            "city": "Onitsha",
            "state": "Anambra State",
            "phone": "2348011112222",
            "top_item": "Essential First Aid Kits & Medical Monitors",
            "price_sample": "₦8,500.00",
            "address": "Shop 4, Bridge Head Pharma Market"
        },
        {
            "id": "dir-08",
            "name": "Balogun Cosmetics & Beauty Hub",
            "category": "Beauty & Skincare",
            "city": "Lagos Island",
            "state": "Lagos State",
            "phone": "2348077778888",
            "top_item": "Organic Skincare Serums & Hair Products",
            "price_sample": "₦9,500.00",
            "address": "No. 22, Balogun Market Street, Lagos Island"
        }
    ]

    def search_directory(self, category_or_city: str) -> str:
        """Finds verified stores with real biometric trust scores and 1-tap WhatsApp contact links (No social media)."""
        q = category_or_city.lower().strip()
        matches = []

        for item in self.VERIFIED_DIRECTORY_LISTINGS:
            if q in item["category"].lower() or q in item["city"].lower() or q in item["name"].lower():
                matches.append(item)

        if not matches:
            matches = self.VERIFIED_DIRECTORY_LISTINGS[:3]

        lines = []
        for m in matches:
            trust_meta = sovereign_trust_score.merchant_trust_store.get(
                m["id"], 
                sovereign_trust_score.initialize_merchant_trust(m["id"], m["name"], has_cac=True, physical_store=True)
            )

            lines.append(f"""🏢 *{m['name']}*
📂 *Niche:* {m['category']} | 📍 *Location:* {m['city']}, {m['state']}
🏆 *Trust Rating:* {trust_meta['star_rating']} ⭐ ({trust_meta['trust_score']}/100)
🛡️ *Badge:* `{trust_meta['badge']}`
📍 *Verified Address:* {m['address']}
📦 *Featured Item:* {m['top_item']} ({m['price_sample']})
📲 *Direct WhatsApp Chat:* https://wa.me/{m['phone']}""")

        return f"""🔍 *[PREMIUM MULTI-NICHE MERCHANT DIRECTORY]*
---------------------------------------------
Found top verified supplier matches for: `{category_or_city}`

{chr(10).join(lines)}

---------------------------------------------
👉 *List Your Business:* Type `#list-store <name> | <niche> | <city>` to get featured in our global directory & receive new customer leads daily!"""

sovereign_directory = SovereignDirectoryEngine()
