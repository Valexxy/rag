package main

import (
	"fmt"
	"strings"
	"time"
)

type NLUSatchMatch struct {
	Matched     bool   `json:"matched"`
	IntentCode  string `json:"intent_code"`
	ResponseMsg string `json:"response_msg"`
}

type LocalNLUEngine struct{}

var globalNLUEngine = &LocalNLUEngine{}

// ResolveLocalNLU attempts to resolve queries locally in <1ms for $0 cost with zero repetitive cards
func (n *LocalNLUEngine) ResolveLocalNLU(query, phone, profileName, businessName string, custLoc CustomerLocation) NLUSatchMatch {
	lower := strings.ToLower(strings.TrimSpace(query))
	if lower == "" {
		return NLUSatchMatch{Matched: false}
	}

	nameStr := profileName
	if nameStr == "" || nameStr == "Valued Client" || strings.HasPrefix(nameStr, "+") {
		nameStr = "there"
	}

	locTag := ""
	if custLoc.City != "" {
		if custLoc.State != "" {
			locTag = fmt.Sprintf("📍 *[%s, %s State]*", custLoc.City, custLoc.State)
		} else {
			locTag = fmt.Sprintf("📍 *[%s]*", custLoc.City)
		}
	}

	// 0. 🧠 DYNAMIC KNOWLEDGE ENGINE CHECK (Learns & grows from Store Manager & Customer Chats)
	if learnedAnswer, found := globalKnowledgeEngine.QueryKnowledgeBase(businessName, query); found {
		return NLUSatchMatch{Matched: true, IntentCode: "LEARNED_KNOWLEDGE_BASE_HIT", ResponseMsg: learnedAnswer}
	}

	timeOfDay := "day"
	hour := time.Now().Hour()
	switch {
	case hour >= 5 && hour < 12:
		timeOfDay = "morning"
	case hour >= 12 && hour < 17:
		timeOfDay = "afternoon"
	default:
		timeOfDay = "evening"
	}

	// 1. 🤝 GREETINGS & SMALL TALK ("hello how is work", "going fine and yours", "good morning", "hi", "how are you")
	if isSmallTalk(lower) {
		if strings.Contains(lower, "yours") || strings.Contains(lower, "fine") || strings.Contains(lower, "good") || strings.Contains(lower, "well") {
			return NLUSatchMatch{Matched: true, IntentCode: "GREETING_SMALLTALK", ResponseMsg: fmt.Sprintf("Everything is going great on my end, thank you! 😊 %s is open and operating at full capacity. What can I get for you today?", businessName)}
		}

		greetings := []string{
			fmt.Sprintf("Hello %s! 👋 Good %s!\n%s\nWe are operating at full capacity serving clients across Nigeria today. How may I assist your solar, electronics, or investment needs?", nameStr, timeOfDay, locTag),
			fmt.Sprintf("Good %s %s! 🌟 Hope your day is going smoothly.\n%s\n%s is open and ready to take your order. What can we get for you today?", timeOfDay, nameStr, locTag, businessName),
			fmt.Sprintf("Hi %s! Warm greetings from %s! 💼\n%s\nEverything is running great today! How can I help you with our product catalog or delivery options?", nameStr, businessName, locTag),
		}
		// Pick deterministic variation based on phone number to prevent string repetition
		idx := int(phoneHash(phone)+uint64(hour)) % len(greetings)
		return NLUSatchMatch{Matched: true, IntentCode: "GREETING_SMALLTALK", ResponseMsg: greetings[idx]}
	}


	// 2. 🛍️ DYNAMIC CATALOG & PRODUCT DISCOVERY (0 HARDCODING — Pulled Live from Database)
	if isCatalogDiscovery(lower) {
		msg := globalKnowledgeEngine.GetDynamicStoreCatalog(businessName, custLoc)
		return NLUSatchMatch{Matched: true, IntentCode: "CATALOG_DISCOVERY", ResponseMsg: msg}
	}


	// 3. 🛠️ OUT-OF-CATALOG / SERVICE REQUESTS ("can you do a market survey for me", "web design", "custom service")
	if isOutOfCatalogRequest(lower) {
		msg := fmt.Sprintf("💼 *[SPECIALIZED STORE CAPABILITIES]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n%s specializes strictly in *Solar Power Systems, High-Capacity Power Banks, Generators, Food Commodities, and Gold Investment Bullion*.\n\nWhile market surveys or non-catalog services are outside our automated automated sales scope, our **Managing Director & Store Manager** handles custom corporate partnerships and bulk sourcing!\n\n📲 *Chat Store Manager Directly:* https://wa.me/2348072015725\n📞 *Direct Call Line:* +234 807 201 5725\n\nHow else may I assist your product order today?", businessName)
		return NLUSatchMatch{Matched: true, IntentCode: "OUT_OF_CATALOG_SERVICE", ResponseMsg: msg}
	}

	// 4. 🏷️ PRODUCT SPECIFIC PRICE & BARGAINING MATCHING
	if strings.Contains(lower, "power bank") || strings.Contains(lower, "20,000") || strings.Contains(lower, "20000") {
		msg := fmt.Sprintf("🔋 *[20,000 mAh SOLAR POWER BANK]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦18,500\n⚡ *Specs:* Rugged outdoor dual USB fast-charging with solar charging panel.\n🤝 *Best Price Offer:* ₦18,500 per unit. For bulk orders (3+ units), our merchant discount gives you ₦17,575 / unit (5%% OFF)!\n\nReply `#buy 2` to order this item now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	if strings.Contains(lower, "solar panel") || strings.Contains(lower, "550w") || (strings.Contains(lower, "panel") && !strings.Contains(lower, "bank")) {
		msg := fmt.Sprintf("☀️ *[550W MONOCRYSTALLINE SOLAR PANEL]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦120,000 per panel\n⚡ *Specs:* Tier-1 High Efficiency Monocrystalline\n🤝 *Best Price Offer:* ₦120,000 / unit.\n\nReply `#buy 1` to order now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	if strings.Contains(lower, "generator") || strings.Contains(lower, "1.5kva") {
		msg := fmt.Sprintf("🔋 *[1.5kVA DUAL SOLAR GENERATOR]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦185,000\n⚡ *Specs:* Silent pure sine wave inverter generator with lithium battery.\n\nReply `#buy 3` to order now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	if strings.Contains(lower, "inverter") || strings.Contains(lower, "3.5kva") {
		msg := fmt.Sprintf("⚡ *[3.5kVA HYBRID SOLAR INVERTER]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦340,000\n⚡ *Specs:* 3.5kVA 24V Pure Sine Wave Hybrid Solar Inverter.\n\nReply `#buy 6` to order now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	if strings.Contains(lower, "rice") || strings.Contains(lower, "50kg") {
		msg := fmt.Sprintf("🌾 *[50kg PREMIUM WHITE RICE BAG]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦60,000 per 50kg bag.\n\nReply `#buy 4` to order now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	if strings.Contains(lower, "gold") || strings.Contains(lower, "bullion") {
		msg := fmt.Sprintf("🥇 *[24K GOLD BAR BULLION (1-GRAM)]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦68,500\n⚡ *Specs:* 999.9 Fine Investment Grade Gold Bullion.\n\nReply `#buy 5` to order now!")
		return NLUSatchMatch{Matched: true, IntentCode: "PRODUCT_PRICE_QUERY", ResponseMsg: msg}
	}

	// 5. 📍 LOCATION & DELIVERY QUERIES ("do you deliver to Anambra/Lagos", "where is your store")
	if strings.Contains(lower, "deliver") || strings.Contains(lower, "waybill") || strings.Contains(lower, "ship") || strings.Contains(lower, "location") || strings.Contains(lower, "branch") {
		msg := fmt.Sprintf("🚚 *[NATIONWIDE NIGERIAN DELIVERY & LOGISTICS]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n%s delivers nationwide across all 36 States & FCT Abuja via our partner logistics carriers (GIG Logistics, ABC Transport, Kwik, & Peace Mass).\n\n📍 *Your Active Shipping Zone:* %s\n📦 *Inter-State Delivery Window:* 24-48 Hours\n\nTo lock in local delivery rates for your order, reply with your item choice (e.g. `#buy 2`)!", businessName, locTag)
		return NLUSatchMatch{Matched: true, IntentCode: "DELIVERY_LOCATION_QUERY", ResponseMsg: msg}
	}

	// 6. 🏦 PAYMENT & BANK DETAILS ("account number", "bank details", "how to pay")
	if strings.Contains(lower, "account") || strings.Contains(lower, "bank") || strings.Contains(lower, "pay") || strings.Contains(lower, "transfer") || strings.Contains(lower, "payment") {
		msg := fmt.Sprintf("💳 *[VERIFIED STORE BANK ACCOUNTS — %s]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏦 *Wema Bank:* 4112328816\n🏦 *Sterling Bank:* 2210094665\n👤 *Account Name:* Teeslux Global Store\n📲 *1-Tap USSD:* `*737*50*4112328816#`\n\nAfter payment, send your transfer receipt screenshot right here for instant verification!", businessName)
		return NLUSatchMatch{Matched: true, IntentCode: "PAYMENT_BANK_QUERY", ResponseMsg: msg}
	}

	return NLUSatchMatch{Matched: false}
}

func isSmallTalk(s string) bool {
	matches := []string{"hello", "hi", "hey", "good morning", "good afternoon", "good evening", "how is work", "how are you", "howdy", "wassup", "sup", "going fine", "fine and yours", "doing well", "all good", "going well", "good day", "how far", "fine thank you", "good thanks", "doing great", "blessed", "fine"}
	for _, m := range matches {
		if s == m || strings.HasPrefix(s, m+" ") || strings.HasSuffix(s, " "+m) || strings.Contains(s, " "+m+" ") {
			return true
		}
	}
	return false
}

func isCatalogDiscovery(s string) bool {
	matches := []string{"what do you sell", "what products", "show catalog", "product list", "what is available", "catalog", "items available", "what can i buy"}
	for _, m := range matches {
		if strings.Contains(s, m) {
			return true
		}
	}
	return false
}

func isOutOfCatalogRequest(s string) bool {
	matches := []string{"market survey", "market check", "market search", "web design", "website", "software app", "graphics design", "marketing campaign", "consultancy", "non catalog", "custom order"}
	for _, m := range matches {
		if strings.Contains(s, m) {
			return true
		}
	}
	return false
}

func phoneHash(s string) uint64 {
	var h uint64 = 14695981039346656037
	for i := 0; i < len(s); i++ {
		h ^= uint64(s[i])
		h *= 1099511628211
	}
	return h
}
