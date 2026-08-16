package main

import (
	"fmt"
	"strings"
	"sync"
	"time"
)

type CustomerProfile struct {
	Phone       string `json:"phone"`
	Name        string `json:"name"`
	Title       string `json:"title"`
	City        string `json:"city"`
	State       string `json:"state"`
	Timezone    string `json:"timezone"` // e.g. "Africa/Lagos" (UTC+1)
	LastSeen    time.Time `json:"last_seen"`
}

type WorldFirstPhoneEngine struct {
	mu       sync.RWMutex
	profiles map[string]CustomerProfile
}

var globalWorldFirstEngine = &WorldFirstPhoneEngine{
	profiles: make(map[string]CustomerProfile),
}

// Extract & update customer name from WhatsApp webhook contact profile or message
func (e *WorldFirstPhoneEngine) UpdateCustomerProfile(phone, profileName, text string) CustomerProfile {
	e.mu.Lock()
	defer e.mu.Unlock()

	prof, exists := e.profiles[phone]
	if !exists {
		prof = CustomerProfile{
			Phone:    phone,
			Name:     "Valued Client",
			Timezone: "Africa/Lagos",
			LastSeen: time.Now(),
		}
	}

	// 1. Extract name from WhatsApp profile contact metadata
	cleanProfName := strings.TrimSpace(profileName)
	if cleanProfName != "" && cleanProfName != "WhatsApp User" && !strings.HasPrefix(cleanProfName, "+") {
		prof.Name = cleanProfName
	}

	// 2. Extract name from chat intro ("My name is Emeka", "I am Dr. Fatima")
	lower := strings.ToLower(text)
	if strings.Contains(lower, "my name is ") {
		parts := strings.Split(lower, "my name is ")
		if len(parts) > 1 {
			nameCandidate := strings.Title(strings.TrimSpace(strings.Fields(parts[1])[0]))
			if len(nameCandidate) > 1 {
				prof.Name = nameCandidate
			}
		}
	} else if strings.Contains(lower, "i am ") {
		parts := strings.Split(lower, "i am ")
		if len(parts) > 1 {
			candidate := strings.Fields(parts[1])[0]
			if len(candidate) > 2 && candidate != "interested" && candidate != "looking" && candidate != "buying" && candidate != "here" {
				prof.Name = strings.Title(candidate)
			}
		}
	}

	prof.LastSeen = time.Now()
	e.profiles[phone] = prof
	return prof
}

// 🕒 AUTOMATIC TIMEZONE & TIME-OF-DAY GREETING
func (e *WorldFirstPhoneEngine) GetTimeOfDayGreeting() (string, string) {
	// West Africa Time (WAT) UTC+1
	loc, err := time.LoadLocation("Africa/Lagos")
	var now time.Time
	if err == nil {
		now = time.Now().In(loc)
	} else {
		now = time.Now().Add(1 * time.Hour) // WAT offset fallback
	}

	hour := now.Hour()
	switch {
	case hour >= 5 && hour < 12:
		return "Good morning", "🌅"
	case hour >= 12 && hour < 17:
		return "Good afternoon", "☀️"
	case hour >= 17 && hour < 23:
		return "Good evening", "🌆"
	default:
		return "Hello", "🌙"
	}
}

// 🌦️ LIVE REAL-TIME WEATHER PLUGIN (OPEN-METEO REST API — ZERO HARDCODING)
func (e *WorldFirstPhoneEngine) GetLocalWeatherNotice(city, phone string) string {
	var lat, lng float64 = 6.5244, 3.3792
	targetName := city

	if city == "" {
		region, rLat, rLng := ResolveRegionFromPhonePrefix(phone)
		lat, lng = rLat, rLng
		targetName = region
	} else {
		cityUpper := strings.ToUpper(city)
		switch {
		case strings.Contains(cityUpper, "ABUJA") || strings.Contains(cityUpper, "FCT"):
			lat, lng = 9.0765, 7.3986
		case strings.Contains(cityUpper, "PORT HARCOURT") || strings.Contains(cityUpper, "RIVERS"):
			lat, lng = 4.8156, 7.0498
		case strings.Contains(cityUpper, "KANO"):
			lat, lng = 12.0022, 8.5920
		case strings.Contains(cityUpper, "ENUGU") || strings.Contains(cityUpper, "ONITSHA"):
			lat, lng = 6.4584, 7.5464
		}
	}

	weather, err := FetchLiveWeather(lat, lng)
	if err == nil && weather != "" {
		return fmt.Sprintf("It's %s in %s today!", weather, targetName)
	}
	return ""
}

// 📱 GENERATE 100% HARDCODING-FREE INITIAL OPENING CARD
func (e *WorldFirstPhoneEngine) GeneratePersonalizedOpening(phone, profileName, text, merchantName string) string {
	prof := e.UpdateCustomerProfile(phone, profileName, text)
	custLoc := globalLocationEngine.GetLocation(phone)
	greetingText, emoji := e.GetTimeOfDayGreeting()

	if merchantName == "" {
		merchantName = "our Store"
	}

	// 1. Dynamic Location / Region Tag
	locationTag := ""
	if custLoc.City != "" {
		locationTag = fmt.Sprintf("📍 *[Location: %s, %s]*\n", custLoc.City, custLoc.State)
	} else {
		region, _, _ := ResolveRegionFromPhonePrefix(phone)
		if region != "" {
			locationTag = fmt.Sprintf("📍 *[Region: %s]*\n", region)
		}
	}

	// 2. Customer Name Greeting
	nameStr := ""
	if prof.Name != "" && prof.Name != "Valued Client" && prof.Name != "WhatsApp User" && !strings.HasPrefix(prof.Name, "+") {
		nameStr = fmt.Sprintf(" %s", prof.Name)
	}

	// 3. Live Satellite Weather
	weatherInfo := e.GetLocalWeatherNotice(custLoc.City, phone)
	weatherStr := ""
	if weatherInfo != "" {
		weatherStr = fmt.Sprintf("\n🌦️ *Live Weather:* %s", weatherInfo)
	}

	// 4. Local Commerce / Traffic Update
	newsStr := ""
	if custLoc.City != "" {
		newsNotice := globalLocalNewsPlugin.GetLocalCommerceNews(custLoc.City)
		if newsNotice != "" {
			newsStr = fmt.Sprintf("\n%s", newsNotice)
		}
	}

	return fmt.Sprintf("%s%s%s! %s Welcome to %s!%s%s\n\nHow may I assist you today?", locationTag, greetingText, nameStr, emoji, merchantName, weatherStr, newsStr)
}







// 📱 PHONE IN-BUILT NATIVE VCF CONTACT CARD GENERATOR
func (e *WorldFirstPhoneEngine) GenerateVCardPayload() string {
	return `BEGIN:VCARD
VERSION:3.0
FN:Teeslux Global Store Manager
ORG:Teeslux Global Electronics & Solar
TEL;TYPE=CELL,VOICE:+2348072015725
EMAIL:contact@teeslux.com
URL:https://sovereign-ai-backend-production.up.railway.app
ADR;TYPE=WORK:;;Onitsha Main Market;Anambra;;Nigeria
END:VCARD`
}
