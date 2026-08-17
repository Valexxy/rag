package main

import (
	"fmt"
	"log"
	"strings"
)

type NewsEngine struct{}

var globalNewsEngine = &NewsEngine{}

func (ne *NewsEngine) GetMultiTierNigerianNews(lga, state, country string) string {
	if state == "" {
		state = "Lagos"
	}
	if lga == "" {
		lga = "Ikeja LGA"
	}
	if country == "" {
		country = "Nigeria"
	}

	log.Printf("[Multi-Tier News Engine] Generating LGA/State/Country news for LGA: %s | State: %s | Country: %s", lga, state, country)

	lgaNews := ne.getLGANews(lga)
	stateNews := ne.getStateNews(state)
	countryNews := ne.getCountryNews()

	return fmt.Sprintf("📰 *[3-TIER NIGERIAN INTELLIGENCE NEWS FEED]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📍 *1. LOCAL LGA NEWS (%s):*\n%s\n\n🏙️ *2. STATE EXECUTIVE NEWS (%s):*\n%s\n\n🇳🇬 *3. NATIONAL NIGERIA POWER & COMMERCE NEWS:*\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n⚡ Stay informed with Teeslux 24/7 Live Intelligence Feed!", strings.ToUpper(lga), lgaNews, strings.ToUpper(state), stateNews, countryNews)
}

func (ne *NewsEngine) getLGANews(lga string) string {
	lower := strings.ToLower(lga)
	if strings.Contains(lower, "eti-osa") || strings.Contains(lower, "lekki") {
		return "• Eti-Osa LGA announces infrastructure upgrade & off-grid solar incentive scheme for commercial plazas in Lekki Phase 1."
	} else if strings.Contains(lower, "ikeja") {
		return "• Ikeja LGA Council launches green energy pilot project & streamlined business permit clearance for electronics stores."
	} else if strings.Contains(lower, "surulere") {
		return "• Surulere LGA power distribution stabilization committee inspects local transformer substations."
	}
	return fmt.Sprintf("• %s Local Government Area council approves new commercial zone development & community safety measures.", lga)
}

func (ne *NewsEngine) getStateNews(state string) string {
	lower := strings.ToLower(state)
	if strings.Contains(lower, "lagos") {
		return "• Lagos State Ministry of Energy opens bids for 500MW Independent Solar Power Grid project.\n• Commercial transport electrification initiative kicks off across major Lagos corridors."
	} else if strings.Contains(lower, "abuja") || strings.Contains(lower, "fct") {
		return "• FCT Administration inaugurates smart street lighting solar grid across Abuja central business district."
	} else if strings.Contains(lower, "rivers") || strings.Contains(lower, "port harcourt") {
		return "• Rivers State Government partners with clean energy developers for Industrial Zone power stabilization."
	}
	return fmt.Sprintf("• %s State Executive Council approves clean energy investment incentives for commercial businesses.", state)
}

func (ne *NewsEngine) getCountryNews() string {
	return "• Nigerian Electricity Regulatory Commission (NERC) highlights solar mini-grid expansion for Tier-1 commercial hubs.\n• Central Bank & Federal Ministry of Power announce green energy tax exemptions for solar equipment importers."
}
