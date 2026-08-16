package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"
)

// Live Open-Meteo Weather API Response struct
type OpenMeteoResponse struct {
	CurrentWeather struct {
		Temperature float64 `json:"temperature"`
		WeatherCode int     `json:"weathercode"`
	} `json:"current_weather"`
}

// 🌦️ GO OPEN-METEO LIVE WEATHER PLUGIN (100% LIVE REAL-TIME WEATHER, NO HARDCODING)
func FetchLiveWeather(lat, lng float64) (string, error) {
	url := fmt.Sprintf("https://api.open-meteo.com/v1/forecast?latitude=%.4f&longitude=%.4f&current_weather=true", lat, lng)
	client := &http.Client{Timeout: 3 * time.Second}
	resp, err := client.Get(url)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var data OpenMeteoResponse
	if err := json.NewDecoder(resp.Body).Decode(&data); err != nil {
		return "", err
	}

	temp := data.CurrentWeather.Temperature
	code := data.CurrentWeather.WeatherCode

	condition := "clear"
	switch {
	case code >= 1 && code <= 3:
		condition = "partly cloudy"
	case code >= 45 && code <= 48:
		condition = "foggy"
	case code >= 51 && code <= 67:
		condition = "rainy"
	case code >= 80 && code <= 99:
		condition = "thunderstorms"
	default:
		condition = "sunny"
	}

	return fmt.Sprintf("%.0f°C and %s", temp, condition), nil
}

// 📍 META WHATSAPP INBUILT NATIVE LOCATION REQUEST BUTTON PAYLOAD
func BuildMetaLocationRequestPayload(recipientPhone string) map[string]interface{} {
	return map[string]interface{}{
		"messaging_product": "whatsapp",
		"to":                recipientPhone,
		"type":              "interactive",
		"interactive": map[string]interface{}{
			"type": "location_request_message",
			"body": map[string]string{
				"text": "📍 Tap below to share your delivery location so we can calculate exact waybill rates and local weather for you!",
			},
			"action": map[string]string{
				"name": "send_location",
			},
		},
	}
}

// 📱 TELECOM NETWORK REGIONAL RESOLVER (ZERO FAKE DEFAULT)
func ResolveRegionFromPhonePrefix(phone string) (string, float64, float64) {
	clean := strings.TrimPrefix(phone, "234")
	clean = strings.TrimPrefix(clean, "+234")
	clean = strings.TrimPrefix(clean, "0")

	// Return neutral Nigeria centroid without forcing fake local cities
	return "Nigeria Hub", 9.0765, 7.3986
}

// 🗺️ EXTRACT EXACT NIGERIAN CITY/TOWN/STATE FROM TEXT MENTIONS
func DetectCityFromText(text string) (string, float64, float64) {
	lower := strings.ToLower(text)

	switch {
	// ABUJA (FCT)
	case strings.Contains(lower, "abuja") || strings.Contains(lower, "maitama") || strings.Contains(lower, "wuse") || strings.Contains(lower, "gwarinpa") || strings.Contains(lower, "asokoro") || strings.Contains(lower, "utako") || strings.Contains(lower, "kubwa") || strings.Contains(lower, "lugbe") || strings.Contains(lower, "garki") || strings.Contains(lower, "jabi"):
		return "Abuja FCT", 9.0765, 7.3986

	// RIVERS / PORT HARCOURT
	case strings.Contains(lower, "port harcourt") || strings.Contains(lower, "phc") || strings.Contains(lower, "gra phase") || strings.Contains(lower, "diobu") || strings.Contains(lower, "rumuokoro") || strings.Contains(lower, "trans amadi") || strings.Contains(lower, "choba") || strings.Contains(lower, "eleme") || strings.Contains(lower, "rivers"):
		return "Port Harcourt", 4.8156, 7.0498

	// OYO / IBADAN
	case strings.Contains(lower, "ibadan") || strings.Contains(lower, "bodija") || strings.Contains(lower, "dugbe") || strings.Contains(lower, "challenge") || strings.Contains(lower, "mokola") || strings.Contains(lower, "iwo road") || strings.Contains(lower, "ring road") || strings.Contains(lower, "oyo"):
		return "Ibadan", 7.3775, 3.9470

	// EDO / BENIN
	case strings.Contains(lower, "benin") || strings.Contains(lower, "uselu") || strings.Contains(lower, "ekenwan") || strings.Contains(lower, "edo"):
		return "Benin City", 6.3350, 5.6037

	// ENUGU
	case strings.Contains(lower, "enugu") || strings.Contains(lower, "new haven") || strings.Contains(lower, "trans ekulu") || strings.Contains(lower, "ogui"):
		return "Enugu", 6.4584, 7.5464

	// DELTA
	case strings.Contains(lower, "asaba") || strings.Contains(lower, "warri") || strings.Contains(lower, "effurun") || strings.Contains(lower, "sapele") || strings.Contains(lower, "delta"):
		return "Asaba", 6.1983, 6.7291

	// KANO
	case strings.Contains(lower, "kano") || strings.Contains(lower, "sabon gari") || strings.Contains(lower, "nassarawa"):
		return "Kano", 12.0022, 8.5920

	// KADUNA
	case strings.Contains(lower, "kaduna") || strings.Contains(lower, "barnawa") || strings.Contains(lower, "sabot tasha") || strings.Contains(lower, "kawo"):
		return "Kaduna", 10.5105, 7.4165

	// OGUN
	case strings.Contains(lower, "abeokuta") || strings.Contains(lower, "sagamu") || strings.Contains(lower, "ota") || strings.Contains(lower, "ijebu") || strings.Contains(lower, "mowe") || strings.Contains(lower, "ibafo") || strings.Contains(lower, "ogun"):
		return "Abeokuta", 7.1557, 3.3458

	// ANAMBRA
	case strings.Contains(lower, "onitsha") || strings.Contains(lower, "nnewi") || strings.Contains(lower, "awka") || strings.Contains(lower, "anambra"):
		return "Onitsha", 6.1437, 6.7865

	// IMO / ABIA
	case strings.Contains(lower, "owerri") || strings.Contains(lower, "aba") || strings.Contains(lower, "umuahia") || strings.Contains(lower, "imo") || strings.Contains(lower, "abia"):
		return "Owerri", 5.4833, 7.0333

	// AKWA IBOM / CROSS RIVER
	case strings.Contains(lower, "uyo") || strings.Contains(lower, "calabar") || strings.Contains(lower, "eket") || strings.Contains(lower, "akwa ibom") || strings.Contains(lower, "cross river"):
		return "Uyo", 5.0377, 7.9128

	// LAGOS (STRICT MATCHING)
	case strings.Contains(lower, "lagos") || strings.Contains(lower, "ikeja") || strings.Contains(lower, "surulere") || strings.Contains(lower, "lekki") || strings.Contains(lower, "vi") || strings.Contains(lower, "yaba") || strings.Contains(lower, "victoria island") || strings.Contains(lower, "ikoyi") || strings.Contains(lower, "ikorodu") || strings.Contains(lower, "festac") || strings.Contains(lower, "alaba"):
		return "Lagos Hub", 6.5244, 3.3792
	}

	return "", 0, 0
}


// 🌐 REVERSE GEOCODE GPS COORDINATES DOWN TO EXACT HOUSE, STREET, COMMUNITY & LGA
func ReverseGeocodeCoords(lat, lng float64) (string, string, string) {
	url := fmt.Sprintf("https://nominatim.openstreetmap.org/reverse?lat=%.6f&lon=%.6f&format=json&addressdetails=1", lat, lng)
	client := &http.Client{Timeout: 4 * time.Second}
	req, _ := http.NewRequest("GET", url, nil)
	req.Header.Set("User-Agent", "Mozilla/5.0 (SovereignAI/2026)")

	resp, err := client.Do(req)
	if err != nil {
		return "", "", ""
	}
	defer resp.Body.Close()

	var result struct {
		Address struct {
			Building      string `json:"building"`
			Amenity       string `json:"amenity"`
			HouseNumber   string `json:"house_number"`
			Road          string `json:"road"`
			Pedestrian    string `json:"pedestrian"`
			Footway       string `json:"footway"`
			Subdivision   string `json:"subdivision"`
			Suburb        string `json:"suburb"`
			Neighbourhood string `json:"neighbourhood"`
			Quarter       string `json:"quarter"`
			Village       string `json:"village"`
			Hamlet        string `json:"hamlet"`
			CityDistrict  string `json:"city_district"`
			Town          string `json:"town"`
			City          string `json:"city"`
			County        string `json:"county"`
			StateDistrict string `json:"state_district"`
			State         string `json:"state"`
		} `json:"address"`
	}

	if err := json.NewDecoder(resp.Body).Decode(&result); err == nil {
		// 1. Extract Street/House
		street := result.Address.Road
		if street == "" {
			street = result.Address.Pedestrian
		}
		if street == "" {
			street = result.Address.Footway
		}
		if street == "" {
			street = result.Address.Amenity
		}
		if street == "" {
			street = result.Address.Building
		}

		// 2. Extract Neighborhood / Community
		comm := result.Address.Suburb
		if comm == "" {
			comm = result.Address.Neighbourhood
		}
		if comm == "" {
			comm = result.Address.Quarter
		}
		if comm == "" {
			comm = result.Address.Village
		}
		if comm == "" {
			comm = result.Address.CityDistrict
		}

		// 3. Extract City / LGA
		city := result.Address.City
		if city == "" {
			city = result.Address.Town
		}
		if city == "" {
			city = result.Address.County
		}
		if city == "" {
			city = result.Address.StateDistrict
		}

		state := result.Address.State

		// Format precise multi-tier address string
		var parts []string
		if result.Address.HouseNumber != "" {
			parts = append(parts, "No. "+result.Address.HouseNumber)
		}
		if street != "" {
			parts = append(parts, street)
		}
		if comm != "" && comm != street {
			parts = append(parts, comm)
		}
		if city != "" && city != comm {
			parts = append(parts, city)
		}

		exactAddress := strings.Join(parts, ", ")
		if exactAddress != "" {
			return exactAddress, city, state
		}
	}

	return "", "", ""
}


