package main

import (
	"fmt"
	"strings"
	"sync"
)

type CustomerLocation struct {
	Phone     string  `json:"phone"`
	City      string  `json:"city"`
	State     string  `json:"state"`
	Landmark  string  `json:"landmark"`
	Latitude  float64 `json:"latitude"`
	Longitude float64 `json:"longitude"`
}

type LocationCommerceEngine struct {
	mu        sync.RWMutex
	locations map[string]CustomerLocation
}

var globalLocationEngine = &LocationCommerceEngine{
	locations: make(map[string]CustomerLocation),
}

// DetectAndUpdateLocation updates customer location dynamically on FIRST CHAT and SUBSEQUENT CHATS
func (l *LocationCommerceEngine) DetectAndUpdateLocation(phone, text string) CustomerLocation {
	l.mu.Lock()
	defer l.mu.Unlock()

	loc, exists := l.locations[phone]
	if !exists {
		loc = CustomerLocation{Phone: phone, City: "Lagos", State: "Lagos"} // Default initial fallback
	}

	lower := strings.ToLower(text)

	// Comprehensive Nigerian City & State dictionary
	cityMap := map[string]struct{ City, State string }{
		"lagos":           {"Lagos", "Lagos"},
		"ikeja":           {"Ikeja", "Lagos"},
		"surulere":        {"Surulere", "Lagos"},
		"lekki":           {"Lekki", "Lagos"},
		"victoria island": {"VI", "Lagos"},
		"yaba":            {"Yaba", "Lagos"},
		"abuja":           {"Abuja", "FCT"},
		"wuse":            {"Wuse", "FCT"},
		"maitama":         {"Maitama", "FCT"},
		"garki":           {"Garki", "FCT"},
		"port harcourt":   {"Port Harcourt", "Rivers"},
		"ph":              {"Port Harcourt", "Rivers"},
		"kano":            {"Kano", "Kano"},
		"dawanau":         {"Dawanau", "Kano"},
		"benin":           {"Benin City", "Edo"},
		"sapele":          {"Sapele", "Delta"},
		"warri":           {"Warri", "Delta"},
		"onitsha":         {"Onitsha", "Anambra"},
		"awka":            {"Awka", "Anambra"},
		"enugu":           {"Enugu", "Enugu"},
		"ibadan":          {"Ibadan", "Oyo"},
		"owerri":          {"Owerri", "Imo"},
		"aba":             {"Aba", "Abia"},
		"calabar":         {"Calabar", "Cross River"},
		"kaduna":          {"Kaduna", "Kaduna"},
		"jos":             {"Jos", "Plateau"},
		"ilorin":          {"Ilorin", "Kwara"},
		"akure":           {"Akure", "Ondo"},
		"abeokuta":        {"Abeokuta", "Ogun"},
		"uyo":             {"Uyo", "Akwa Ibom"},
		"asaba":           {"Asaba", "Delta"},
	}

	for kw, mapping := range cityMap {
		if strings.Contains(lower, kw) {
			loc.City = mapping.City
			loc.State = mapping.State
			loc.Landmark = strings.Title(kw)
			l.locations[phone] = loc
			break
		}
	}

	l.locations[phone] = loc
	return loc
}

func (l *LocationCommerceEngine) GetLocation(phone string) CustomerLocation {
	l.mu.RLock()
	defer l.mu.RUnlock()

	loc, exists := l.locations[phone]
	if !exists {
		return CustomerLocation{Phone: phone, City: "Lagos", State: "Lagos"}
	}
	return loc
}

// FEATURE 5: Neighborhood Group Buy & Co-Op Buying Generator
func (l *LocationCommerceEngine) GenerateNeighborhoodGroupBuyNotice(phone string) string {
	loc := l.GetLocation(phone)
	return fmt.Sprintf("🎉 *[NEIGHBORHOOD GROUP BUY — %s]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n3 buyers in *%s (%s State)* are currently pooling an order for 550W Monocrystalline Solar Panels!\n\nJoin their group pool before 6:00 PM today to unlock **12%% GROUP DISCOUNT (₦105,600/panel)** and split waybill shipping costs!\n\nReply `#buy group` to join the pool!", strings.ToUpper(loc.City), loc.City, loc.State)
}

// FEATURE 6: Hyper-Local Dialect & Pidgin Tone Personalizer
func (l *LocationCommerceEngine) ApplyDialectTone(phone, responseText string) string {
	loc := l.GetLocation(phone)
	stateUpper := strings.ToUpper(loc.State)
	cityUpper := strings.ToUpper(loc.City)

	var greeting string
	switch {
	case strings.Contains(stateUpper, "EDO") || strings.Contains(stateUpper, "DELTA") || strings.Contains(cityUpper, "BENIN") || strings.Contains(cityUpper, "WARRI") || strings.Contains(cityUpper, "SAPELE"):
		greeting = fmt.Sprintf("📍 *[Location Detected: %s, %s]*\nHow body my boss! For your location at %s, express waybill delivery takes just 24 hours!\n\n", loc.City, loc.State, loc.City)
	case strings.Contains(stateUpper, "FCT") || strings.Contains(cityUpper, "ABUJA"):
		greeting = fmt.Sprintf("📍 *[Executive Service: %s, FCT]*\nGood day Executive! For delivery to %s, our VIP courier unit ensures 24-hour white-glove delivery.\n\n", loc.City, loc.City)
	case strings.Contains(stateUpper, "KANO") || strings.Contains(stateUpper, "KADUNA"):
		greeting = fmt.Sprintf("📍 *[Location Detected: %s, Northern Hub]*\nSannu da zuwa! For our esteemed customer in %s, direct logistics dispatch is available daily.\n\n", loc.City, loc.City)
	case strings.Contains(stateUpper, "RIVERS") || strings.Contains(cityUpper, "PORT HARCOURT"):
		greeting = fmt.Sprintf("📍 *[Location Detected: %s, Rivers State]*\nGreat day Boss! Fast logistics dispatch to %s is ready for immediate fulfillment.\n\n", loc.City, loc.City)
	default:
		greeting = fmt.Sprintf("📍 *[Location Detected: %s, %s]*\nWelcome! Doorstep delivery to %s is available via our express delivery network.\n\n", loc.City, loc.State, loc.City)
	}

	return greeting + responseText
}
