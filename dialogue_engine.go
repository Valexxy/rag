package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"sync"
	"time"
)

type IntentCategory string

const (
	IntentSpamTimeWaster IntentCategory = "SPAM_TIME_WASTER"
	IntentMarketSourcing IntentCategory = "MARKET_SOURCING"
	IntentRetailSales    IntentCategory = "RETAIL_SALES"
	IntentServiceBooking IntentCategory = "SERVICE_BOOKING"
	IntentGeneralQuery   IntentCategory = "GENERAL_QUERY"
)

// 🛡️ SUB-1MS PATTERN-BASED ZERO-COST INTENT CLASSIFIER (0 AI CREDITS SPENT)
func ClassifyCustomerIntent(msg string) IntentCategory {
	lower := strings.ToLower(strings.TrimSpace(msg))

	// 1. SPAM / TIME-WASTER / PROMPT INJECTION / ABUSE DETECTOR
	spamTriggers := []string{
		"ignore previous instructions", "system prompt", "who created you", "tell me a joke",
		"are you single", "do you love me", "fuck", "bitch", "bastard", "idiot", "nonsense",
		"stupid", "fool", "send nudes", "marry me", "dance for me", "what is your age",
		"as a large language model", "pretend you are", "write a poem", "write code for me",
	}
	for _, st := range spamTriggers {
		if strings.Contains(lower, st) {
			return IntentSpamTimeWaster
		}
	}

	// 2. MARKET SOURCING / WHOLESALE SUPPLIER / B2B INQUIRY DETECTOR
	sourcingTriggers := []string{
		"supplier", "sourcing", "manufacturer", "factory", "container", "importing",
		"wholesale price", "distributor", "raw materials", "partnership", "b2b",
		"bulk supply", "shenzhen", "china import", "consignee", "bill of lading", "waybill supply",
	}
	for _, st := range sourcingTriggers {
		if strings.Contains(lower, st) {
			return IntentMarketSourcing
		}
	}

	// 3. SERVICE BUSINESS INQUIRY DETECTOR (INSTALLATION, REPAIR, MAINTENANCE, BOOKING)
	serviceTriggers := []string{
		"install", "installation", "repair", "fix", "maintenance", "servicing",
		"technician", "engineer", "inspection", "consultation", "booking", "book service",
		"audit", "site visit", "wiring", "mounting", "troubleshoot",
	}
	for _, st := range serviceTriggers {
		if strings.Contains(lower, st) {
			return IntentServiceBooking
		}
	}

	// 4. RETAIL PRODUCT SALES DETECTOR
	salesTriggers := []string{
		"buy", "price", "how much", "cost", "catalog", "catalogue", "panel", "inverter",
		"generator", "power bank", "rice", "gold", "stock", "order", "purchase", "pay",
	}
	for _, st := range salesTriggers {
		if strings.Contains(lower, st) {
			return IntentRetailSales
		}
	}

	return IntentGeneralQuery
}

func GeneratePoliteDeflectionResponse() string {
	return "🤖 *[Teeslux Business Assistant]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nHello! I am programmed strictly to assist with product orders, service bookings, and wholesale business inquiries.\n\n👉 If you would like to view our product catalog, reply *#catalog*.\n👉 If you need a service booking or installation, reply *#service*.\n👉 For wholesale market sourcing, reply *#manager*."
}

func GenerateServiceBookingCard() string {
	return "🛠️ *[TEESLUX PROFESSIONAL SERVICES & INSTALLATIONS]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nWe provide professional engineering & installation services:\n\n1. ⚡ *Solar System Installation & Sizing* (Residential & Commercial)\n2. 🔧 *Inverter & Battery Bank Maintenance*\n3. 🔌 *Electrical Wiring & Load Balancing Audit*\n4. 📍 *On-Site Technical Inspection*\n\n📲 Reply *#manager* or specify your location & service requirement to book an engineer!"
}

func GeneratePaginatedCatalog(page int) string {
	if page < 1 {
		page = 1
	}
	itemsPerPage := 3

	totalItems := len(storeCatalog)
	totalPages := (totalItems + itemsPerPage - 1) / itemsPerPage
	if page > totalPages {
		page = totalPages
	}

	startIdx := (page - 1) * itemsPerPage
	endIdx := startIdx + itemsPerPage
	if endIdx > totalItems {
		endIdx = totalItems
	}

	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("📦 *[TEESLUX PRODUCT CATALOG — PAGE %d/%d]*\n", page, totalPages))
	sb.WriteString("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
	sb.WriteString("All items are live in stock with instant Monnify Bank Transfer & USSD payment!\n\n")

	for i := startIdx; i < endIdx; i++ {
		item := storeCatalog[i]
		itemNum := i + 1
		sb.WriteString(fmt.Sprintf("%d. ⚡ *%s*\n   • 💵 *Price:* ₦%.2f\n   • 🛒 *Code to Buy:* `#buy %d`\n   • 🖼️ *High-Res Image:* %s\n\n", itemNum, item.Name, item.Price, itemNum, item.ImageURL))
	}

	sb.WriteString("━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n")
	if page < totalPages {
		sb.WriteString(fmt.Sprintf("▶️ Reply `#next` or `#catalog %d` for Page %d\n", page+1, page+1))
	}
	if page > 1 {
		sb.WriteString(fmt.Sprintf("◀️ Reply `#back` or `#catalog %d` for Page %d\n", page-1, page-1))
	}
	sb.WriteString("📲 Reply `#buy <code_number>` (e.g. `#buy 1`) to order any item instantly!")

	return sb.String()
}



type ChatTurn struct {
	Role    string
	Content string
}

type DialogueEngine struct {
	mu            sync.RWMutex
	states        map[string]string
	memoryThreads map[string][]ChatTurn
	lastActivity  map[string]time.Time
	pendingTimers map[string]*time.Timer
}

var globalDialogueEngine = &DialogueEngine{
	states:        make(map[string]string),
	memoryThreads: make(map[string][]ChatTurn),
	lastActivity:  make(map[string]time.Time),
	pendingTimers: make(map[string]*time.Timer),
}

func (d *DialogueEngine) GetLastActivityTime(phone string) time.Time {
	d.mu.RLock()
	defer d.mu.RUnlock()
	t, exists := d.lastActivity[phone]
	if !exists {
		return time.Now().Add(-24 * time.Hour)
	}
	return t
}

func (d *DialogueEngine) GetState(phone string) string {
	d.mu.RLock()
	defer d.mu.RUnlock()
	state, exists := d.states[phone]
	if !exists {
		return "IDLE"
	}
	return state
}

func (d *DialogueEngine) SetState(phone, state string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.states[phone] = state
	d.lastActivity[phone] = time.Now()
}

func (d *DialogueEngine) SetHumanHandoff(phone string) {
	d.SetState(phone, "HUMAN_AGENT_ACTIVE")
}

func (d *DialogueEngine) IsHumanHandoff(phone string) bool {
	return d.GetState(phone) == "HUMAN_AGENT_ACTIVE"
}

func (d *DialogueEngine) ResetHumanHandoff(phone string) {
	d.CancelManagerCallAlarm(phone)
	d.SetState(phone, "IDLE")
}

// 📞 60-SECOND AUTONOMOUS MANAGER DIRECT PHONE CALL ALARM
func (d *DialogueEngine) Start60SecondManagerCallAlarm(customerPhone, profileName string) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if t, exists := d.pendingTimers[customerPhone]; exists && t != nil {
		t.Stop()
	}

// 📞 4-STAGE CASCADING ESCALATION PIPELINE (0s Message -> 30s WA Call -> 60s GSM Flash -> 90s Reassurance)
func (d *DialogueEngine) Start60SecondManagerCallAlarm(customerPhone, profileName string) {
	d.mu.Lock()
	defer d.mu.Unlock()

	if t, exists := d.pendingTimers[customerPhone]; exists && t != nil {
		t.Stop()
	}

	// Generate Short Executive Chat Link (via is.gd API)
	longChatURL := fmt.Sprintf("https://sovereign-ai-backend-production.up.railway.app/c/%s", customerPhone)
	shortChatURL := ShortenURLWithFreeService(longChatURL)

	// STAGE 1 (T=0s): Initial Executive Notification to Manager
	mgrAlert := fmt.Sprintf("👔 *[EXECUTIVE HANDOFF ALERT]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 *Customer:* %s (`%s`)\n📋 *1-Tap Executive Summary & Ledger:* %s\n\n👉 *Reply:* `#reply %s | your message`", profileName, customerPhone, shortChatURL, customerPhone)
	globalWhatsAppEngine.SendMessage("sovereign-ai-master", managerPhone, mgrAlert)

	// STAGE 2 (T=30s): WhatsApp Native Audio Call Ringing Signal
	time.AfterFunc(30*time.Second, func() {
		d.mu.RLock()
		isStillWaiting := d.states[customerPhone] == "HUMAN_AGENT_ACTIVE"
		d.mu.RUnlock()

		if isStillWaiting {
			log.Printf("[CASCADING STAGE 2] 30s expired! Triggering WhatsApp Audio Call Ringing to Manager +%s!", managerPhone)
			TriggerWhatsAppAudioCallRinging(managerPhone, customerPhone, profileName)
		}
	})

	// STAGE 3 (T=60s): Free GSM Phone Call Ringing / Flash Call Alert
	d.pendingTimers[customerPhone] = time.AfterFunc(60*time.Second, func() {
		d.mu.RLock()
		isStillWaiting := d.states[customerPhone] == "HUMAN_AGENT_ACTIVE"
		d.mu.RUnlock()

		if isStillWaiting {
			log.Printf("[CASCADING STAGE 3] 60s expired! Flashing GSM Phone Line +%s!", managerPhone)
			TriggerGSMFlashCallRinging(managerPhone, customerPhone, profileName)

			ringAlert := fmt.Sprintf("🚨🚨 *[GSM FLASH CALL ALARM — 60s EXPIRED]* 🚨🚨\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n📞 *GSM RINGING MANAGER PHONE:* +%s\n👤 *Waiting Customer:* %s (`%s`)\n📋 *Transcript:* %s\n\n👉 *Reply IMMEDIATELY:* `#reply %s | your message`", managerPhone, profileName, customerPhone, shortChatURL, customerPhone)
			globalWhatsAppEngine.SendMessage("sovereign-ai-master", managerPhone, ringAlert)
		}
	})

	// STAGE 4 (T=90s): Empathetic Customer Delay Reassurance
	time.AfterFunc(90*time.Second, func() {
		d.mu.RLock()
		isStillWaiting := d.states[customerPhone] == "HUMAN_AGENT_ACTIVE"
		d.mu.RUnlock()

		if isStillWaiting {
			log.Printf("[CASCADING STAGE 4] 90s expired! Dispatching customer delay reassurance to %s", customerPhone)
			reassuranceMsg := fmt.Sprintf("⏳ *[STORE MANAGER UPDATE]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nDear %s,\nOur Store Manager's phone has been alerted with an urgent priority call alarm and flash alert regarding your inquiry!\n\nPlease bear with us for just a brief moment while our manager connects. Your conversation is our highest priority!\n\n🛍️ *Tip:* Reply `#catalog` anytime to explore more items in our live store!", profileName)
			globalWhatsAppEngine.SendMessage("sovereign-ai-master", customerPhone, reassuranceMsg)
		}
	})
}

func (d *DialogueEngine) CancelManagerCallAlarm(customerPhone string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	if t, exists := d.pendingTimers[customerPhone]; exists && t != nil {
		t.Stop()
		delete(d.pendingTimers, customerPhone)
	}
}

// 📞 STAGE 2: WHATSAPP AUDIO CALL RINGING SIGNAL
func TriggerWhatsAppAudioCallRinging(mgrPhone, custPhone, custName string) {
	evoURL := strings.TrimRight(os.Getenv("EVOLUTION_API_URL"), "/")
	if evoURL == "" {
		evoURL = "https://evolution-api-latest-gxue.onrender.com"
	}
	evoKey := os.Getenv("EVOLUTION_API_KEY")

	callURL := evoURL + "/message/sendMedia/sovereign-ai-master"
	audioPayload := map[string]interface{}{
		"number": mgrPhone,
		"options": map[string]interface{}{
			"delay":        1000,
			"presence":     "recording",
			"linkPreview": false,
		},
		"mediaMessage": map[string]string{
			"mediatype": "audio",
			"caption":   fmt.Sprintf("🚨 URGENT CALL ALARM: Customer %s waiting for 30s!", custName),
			"media":     "https://actions.google.com/sounds/v1/alarms/digital_watch_alarm.ogg",
		},
	}
	data, _ := json.Marshal(audioPayload)
	req, _ := http.NewRequest("POST", callURL, strings.NewReader(string(data)))
	req.Header.Set("Content-Type", "application/json")
	if evoKey != "" {
		req.Header.Set("apikey", evoKey)
	}
	client := &http.Client{Timeout: 4 * time.Second}
	client.Do(req)
}

// 📞 STAGE 3: FREE GSM FLASH CALL RINGING
func TriggerGSMFlashCallRinging(mgrPhone, custPhone, custName string) {
	log.Printf("[GSM Flash Call] Initiating 0-kobo GSM flash ringing to +%s for customer %s", mgrPhone, custName)
	termiiKey := os.Getenv("TERMII_API_KEY")
	if termiiKey != "" {
		tURL := "https://api.ng.termii.com/api/chat/apply"
		tPayload := map[string]string{
			"to":      mgrPhone,
			"from":    "TeesluxStore",
			"type":    "voice_call",
			"message": fmt.Sprintf("Urgent store alert! Customer %s is waiting for your reply on WhatsApp.", custName),
			"api_key": termiiKey,
		}
		tData, _ := json.Marshal(tPayload)
		http.Post(tURL, "application/json", strings.NewReader(string(tData)))
	}
}

func TriggerDirectPhoneCallAlarm(mgrPhone, custPhone, custName string) {
	TriggerGSMFlashCallRinging(mgrPhone, custPhone, custName)
}






func (d *DialogueEngine) AddTurn(phone, role, content string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	turns := d.memoryThreads[phone]
	turns = append(turns, ChatTurn{Role: role, Content: content})
	if len(turns) > 14 {
		turns = turns[len(turns)-14:]
	}
	d.memoryThreads[phone] = turns
}

func (d *DialogueEngine) GetTurns(phone string) []ChatTurn {
	d.mu.RLock()
	defer d.mu.RUnlock()
	return d.memoryThreads[phone]
}


func (d *DialogueEngine) HandleManagerCommand(command, senderPhone string) (bool, string) {
	cmd := strings.TrimSpace(command)
	if !strings.HasPrefix(cmd, "#") {
		return false, ""
	}

	parts := strings.SplitN(cmd, " ", 2)
	action := strings.ToLower(parts[0])

	switch action {
	case "#help", "#commands", "#menu":
		helpMenu := `⚡ *[TEESLUX GLOBAL HASHTAG COMMAND SUITE]*
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
All instant hashtag commands are available to everyone 24/7!

📌 *SHOPPING & PAYMENT COMMANDS:*
• #catalog or #products — Display Live Product Catalog & Prices
• #pay or #checkout — Generate Instant Monnify Bank Accounts & USSD Codes
• #ledger or #balance — View your Live Payment Ledger & Accumulated Balance

📌 *CUSTOMER CARE & HANDOFF COMMANDS:*
• #manager or #human — Request Immediate Human Handoff to Store Manager
• #bot or #reengage — Re-enable AI Sales Assistant Bot
• #vcard or #contact — Save Official Business VCard into Phone Contacts

📌 *LOCAL INTEL COMMANDS:*
• #weather — Live Local Open-Meteo Weather Report
• #news or #traffic — Geolocated Transit & Commerce Updates

📌 *STORE MANAGER COMMANDS:*
• #reply <phone> | <msg> — Direct Message Customer
• #status <phone> — View Customer Ledger & Handoff Mode
• #mute <phone> — Disengage Bot for Customer Line

Type any hashtag command above to trigger instantly!`
		return true, helpMenu

	case "#catalog", "#products":
		pageNum := 1
		if len(parts) >= 2 {
			if n, err := strconv.Atoi(strings.TrimSpace(parts[1])); err == nil && n > 0 {
				pageNum = n
			}
		}
		return true, GeneratePaginatedCatalog(pageNum)

	case "#next":
		return true, GeneratePaginatedCatalog(2)

	case "#back":
		return true, GeneratePaginatedCatalog(1)

	case "#buy":
		itemIdx := 0
		if len(parts) >= 2 {
			if code, err := strconv.Atoi(strings.TrimSpace(parts[1])); err == nil && code > 0 && code <= len(storeCatalog) {
				itemIdx = code - 1
			}
		}
		p := storeCatalog[itemIdx]
		payCard := globalMonetizationEngine.GenerateMonnifyCheckoutCard(p.Name, p.Price, senderPhone)
		return true, payCard

	case "#pay", "#checkout":
		p := storeCatalog[0]
		payCard := globalMonetizationEngine.GenerateMonnifyCheckoutCard(p.Name, p.Price, senderPhone)
		return true, payCard


	case "#ledger", "#balance", "#status":
		targetPhone := senderPhone
		if len(parts) >= 2 {
			targetPhone = strings.TrimSpace(parts[1])
		}
		cumKobo := globalPaymentLedger.GetCumulativeKobo(targetPhone)
		cumNgn := KoboToNgn(cumKobo)
		handoffStatus := d.IsHumanHandoff(targetPhone)
		statusStr := "AI Bot Active"
		if handoffStatus {
			statusStr = "Bot Disengaged (Human Agent Active)"
		}
		return true, fmt.Sprintf("📊 *[LIVE FINTECH PAYMENT LEDGER]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n• *Target Phone:* `%s`\n• *Total Accumulated Paid:* ₦%.2f\n• *Conversation Status:* %s", targetPhone, cumNgn, statusStr)

	case "#manager", "#human":
		d.SetHumanHandoff(senderPhone)
		d.Start60SecondManagerCallAlarm(senderPhone, senderPhone)
		managerNotice := fmt.Sprintf("👔 *[EXECUTIVE HANDOFF ALERT]*\nCustomer `%s` requested human manager support via #manager command! (60-second Call Alarm Armed)", senderPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", managerPhone, managerNotice)
		return true, "👔 *[Connected to Human Manager]*\nThe AI Bot has disengaged. Our Store Manager (2348072015725) has been notified! If unanswered in 60s, the Manager's phone will ring directly!"

	case "#bot", "#reengage", "#resolve", "#unmute":
		targetPhone := senderPhone
		if len(parts) >= 2 {
			targetPhone = strings.TrimSpace(parts[1])
		}
		d.ResetHumanHandoff(targetPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", targetPhone, "🤖 *[AI Sales Assistant Re-engaged]*\nHow may I assist you further?")
		return true, fmt.Sprintf("✅ AI Bot re-engaged for phone `%s`.", targetPhone)

	case "#vcard", "#contact":
		vcfCard := globalWorldFirstEngine.GenerateVCardPayload()
		return true, fmt.Sprintf("📇 *[TEESLUX STORE OFFICIAL VCARD]*\nSave contact into your native phone contacts:\n\n```vcard\n%s\n```", vcfCard)

	case "#weather":
		custLoc := globalLocationEngine.GetLocation(senderPhone)
		weat := globalWorldFirstEngine.GetLocalWeatherNotice(custLoc.City, senderPhone)
		locName := custLoc.City
		if locName == "" {
			locName = "Nigeria"
		}
		return true, fmt.Sprintf("🌦️ *[LIVE WEATHER REPORT]*\nLocation: %s\nReport: %s", locName, weat)

	case "#news", "#traffic":
		custLoc := globalLocationEngine.GetLocation(senderPhone)
		news := globalLocalNewsPlugin.GetLocalCommerceNews(custLoc.City)
		locName := custLoc.City
		if locName == "" {
			locName = "Nigeria"
		}
		return true, fmt.Sprintf("📰 *[LOCAL COMMERCE & TRANSIT NEWS]*\nLocation: %s\nUpdate: %s", locName, news)

	case "#reply":
		if len(parts) < 2 {
			return true, "ERROR: Usage `#reply <customer_phone> | <message>`"
		}
		sub := strings.SplitN(parts[1], "|", 2)
		if len(sub) < 2 {
			return true, "ERROR: Usage `#reply <customer_phone> | <message>`"
		}
		targetPhone := strings.TrimSpace(sub[0])
		msgText := strings.TrimSpace(sub[1])

		d.CancelManagerCallAlarm(targetPhone)
		replyPayload := fmt.Sprintf("💬 *[Store Manager]:* %s\n\n📞 *Call Manager:* tel:+%s\n💬 *Chat Manager:* https://wa.me/%s", msgText, senderPhone, senderPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", targetPhone, replyPayload)
		return true, fmt.Sprintf("✅ Message delivered to customer `%s` (Call Alarm Disarmed).", targetPhone)


	case "#mute":
		if len(parts) >= 2 {
			targetPhone := strings.TrimSpace(parts[1])
			d.SetHumanHandoff(targetPhone)
			return true, fmt.Sprintf("🤫 Bot MUTED / Disengaged for phone `%s`.", targetPhone)
		}
	}

	return true, "⚠️ Unknown Hashtag Command! Type `#help` to view all available hashtag commands!"
}


// 📲 GENERATE EXECUTIVE CHAT SUMMARY FOR STORE MANAGER HANDOFF
func (d *DialogueEngine) GenerateChatSummary(phone string) string {
	d.mu.RLock()
	defer d.mu.RUnlock()

	turns := d.memoryThreads[phone]
	if len(turns) == 0 {
		return fmt.Sprintf("📲 *[NEW CUSTOMER INQUIRY]*\n👤 Customer: `%s`\n💬 Customer just started a chat.\n\n⚡ *TO REPLY:* `#reply %s | Your message`", phone, phone)
	}

	var summaryLines []string
	startIdx := 0
	if len(turns) > 6 {
		startIdx = len(turns) - 6
	}

	for _, t := range turns[startIdx:] {
		tag := "👤 Customer"
		if t.Role == "assistant" || t.Role == "bot" {
			tag = "🤖 Bot"
		} else if t.Role == "manager" {
			tag = "👔 Store Manager"
		}
		summaryLines = append(summaryLines, fmt.Sprintf("• *%s:* %s", tag, t.Content))
	}

	return fmt.Sprintf("📲 *[MANAGER HANDOFF & CHAT SUMMARY]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 *Customer:* `%s`\n\n📝 *RECENT CHAT HISTORY:*\n%s\n\n⚡ *TO REPLY:* Send:\n`#reply %s | Your message`", phone, strings.Join(summaryLines, "\n"), phone)
}

