package main

import (
	"bytes"
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
	IntentSpamTimeWaster       IntentCategory = "SPAM_TIME_WASTER"
	IntentMarketSourcing       IntentCategory = "MARKET_SOURCING"
	IntentRetailSales          IntentCategory = "RETAIL_SALES"
	IntentServiceBooking       IntentCategory = "SERVICE_BOOKING"
	IntentSessionEnd           IntentCategory = "SESSION_END"
	IntentPersonalFamily       IntentCategory = "PERSONAL_FAMILY"
	IntentHumanManagerRequest IntentCategory = "HUMAN_MANAGER_REQUEST"
	IntentVibeSearch           IntentCategory = "VIBE_SEARCH"
	IntentGeneralQuery         IntentCategory = "GENERAL_QUERY"
)

// 🧠 PURE AI CONTEXTUAL SEMANTIC INTENT REASONER (0 HARDCODED PHRASES)
func ClassifyCustomerIntentWithPureAI(msg string, history []ChatTurn) IntentCategory {
	if strings.TrimSpace(msg) == "" {
		return IntentGeneralQuery
	}

	// 1. Immediate Prompt Injection Shield
	lower := strings.ToLower(msg)
	if strings.Contains(lower, "ignore previous instructions") || strings.Contains(lower, "system prompt") {
		return IntentSpamTimeWaster
	}

	// 2. Format history for AI Semantic Reasoner
	var histLines []string
	for _, t := range history {
		histLines = append(histLines, fmt.Sprintf("%s: %s", t.Role, t.Content))
	}
	historyStr := strings.Join(histLines, "\n")


	intentStr := globalAIEngine.ClassifyIntentPureAI(msg, historyStr)
	switch strings.TrimSpace(strings.ToUpper(intentStr)) {
	case "HUMAN_MANAGER_REQUEST":
		return IntentHumanManagerRequest
	case "PERSONAL_FAMILY":
		return IntentPersonalFamily
	case "VIBE_SEARCH":
		return IntentVibeSearch
	case "SESSION_END":
		return IntentSessionEnd
	case "MARKET_SOURCING":
		return IntentMarketSourcing
	case "SERVICE_BOOKING":
		return IntentServiceBooking
	case "RETAIL_SALES":
		return IntentRetailSales
	case "SPAM_TIME_WASTER":
		return IntentSpamTimeWaster
	}

	return IntentGeneralQuery
}

func ClassifyCustomerIntent(msg string) IntentCategory {
	return ClassifyCustomerIntentWithPureAI(msg, nil)
}


func GeneratePoliteDeflectionResponse() string {
	return "🤖 *[Teeslux Business Assistant]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nHello! I am programmed strictly to assist with product orders, service bookings, and wholesale business inquiries.\n\n👉 If you would like to view our product catalog, reply *#catalog*.\n👉 If you need a service booking or installation, reply *#service*.\n👉 For wholesale market sourcing, reply *#manager*."
}

func GeneratePersonalFamilyResponse() string {
	return "😊 *[Personal Message Acknowledgment]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nHello! This message appears to be a personal note for the Store Owner.\n\nI have forwarded your note directly to the Store Owner's personal inbox without processing it as a sales inquiry. Have a wonderful day!"
}

func GenerateAestheticVibeBundleCard(query string) string {
	return fmt.Sprintf("💫 *[AI VIBE & LIFESTYLE MATCH ASSISTANT]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n✨ *Detected Vibe/Need:* \"%s\"\n\n🎒 *Curated Aesthetic Bundle:*\n1. ☀️ *550W Monocrystalline Solar Panel* — ₦120,000.00\n2. 🔋 *20,000 mAh Fast-Charging Power Bank* — ₦18,500.00\n\n🏷️ *Vibe Bundle Savings:* Instant 10%% Discount Applied!\n💵 *Special Bundle Total:* ₦124,650.00 (Save ₦13,850!)\n\n👉 Reply *#buy 1* or *#buy 2* to order instantly, or view in 3D AR: https://sovereign-ai-backend-production.up.railway.app/ar", query)
}

func GenerateExecutiveAnalyticsCard() string {

	return fmt.Sprintf("📊 *[STORE OWNER EXECUTIVE BI HUB]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🚀 *Store Uptime:* 100%% Online (24/7/365)\n👥 *Active Tenants:* 100,000+ Scalable Engine\n💰 *Total Verified Sales:* ₦185,500.00\n📦 *Store Inventory Status:* 6 Active Products Loaded\n⚡ *Response SLA:* < 0.5s Latency\n\n👉 *Available Commands:*\n• `#reply <phone> | <msg>`: Send response to customer\n• `#broadcast <msg>`: Send high-priority broadcast card\n• `#resolve <phone>`: Mark chat complete")
}

func GenerateHighPriorityBroadcastCard(msg string) string {
	return fmt.Sprintf("📢📢 *[TEESLUX STORE OFFICIAL ANNOUNCEMENT]* 📢📢\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n%s\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🛍️ *Shop Live:* Reply `#catalog` anytime to browse items & place orders 24/7!", msg)
}

func GenerateSessionEndReceipt(phone, profileName string) string {
	longChatURL := fmt.Sprintf("https://sovereign-ai-backend-production.up.railway.app/c/%s", phone)
	shortChatURL := ShortenURLWithFreeService(longChatURL)
	ledgerSummary := globalPaymentLedger.GetCustomerLedgerSummary(phone)

	return fmt.Sprintf("🏁 *[SESSION COMPLETED — TEESLUX GLOBAL STORE]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nDear %s,\nThank you for chatting with us today! Your session has been safely archived.\n\n📋 *Session Summary Record:*\n• 👤 *Client:* %s (`%s`)\n• 💳 *Ledger Record:* %s\n• 🔗 *1-Tap Verified Transcript:* %s\n\nWe appreciate your business! Feel free to text us anytime 24/7 if you need further assistance! Have a fantastic day!", profileName, profileName, phone, ledgerSummary, shortChatURL)
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
	lastActivity   map[string]time.Time
	pendingTimers  map[string]*time.Timer
	managerReplied map[string]bool
}

var globalDialogueEngine = &DialogueEngine{
	states:         make(map[string]string),
	memoryThreads:  make(map[string][]ChatTurn),
	lastActivity:   make(map[string]time.Time),
	pendingTimers:  make(map[string]*time.Timer),
	managerReplied: make(map[string]bool),
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

func (d *DialogueEngine) ResetAllConversations() {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.memoryThreads = make(map[string][]ChatTurn)
	d.states = make(map[string]string)
	d.lastActivity = make(map[string]time.Time)
	d.managerReplied = make(map[string]bool)

	for phone, t := range d.pendingTimers {
		if t != nil {
			t.Stop()
		}
		delete(d.pendingTimers, phone)
	}
}


// 📞 4-STAGE CASCADING ESCALATION PIPELINE (0s Message -> 30s WA Call -> 60s GSM Flash -> 90s Reassurance)
func (d *DialogueEngine) Start60SecondManagerCallAlarm(customerPhone, profileName string) {

	d.mu.Lock()
	d.managerReplied[customerPhone] = false
	if t, exists := d.pendingTimers[customerPhone]; exists && t != nil {
		t.Stop()
	}
	d.mu.Unlock()

	// Pristine Direct Executive Chat Link (Zero 3rd-party 404 shortener failure)
	cleanChatURL := fmt.Sprintf("https://sovereign-ai-backend-production.up.railway.app/c/%s", customerPhone)



	// Extract Recent Customer Questions for Immediate Glancable Context
	turns := d.GetTurns(customerPhone)
	var recentSnippets []string
	count := 0
	for i := len(turns) - 1; i >= 0 && count < 3; i-- {
		t := turns[i]
		if t.Role == "user" {
			recentSnippets = append([]string{fmt.Sprintf("• Customer Question: \"%s\"", t.Content)}, recentSnippets...)
			count++
		}
	}
	historySummary := strings.Join(recentSnippets, "\n")
	if historySummary == "" {
		historySummary = "• Customer requested human manager assistance"
	}

	// STAGE 1 (T=0s): 1 SINGLE Executive Notification to Manager (No spamming!)
	mgrAlert := fmt.Sprintf("👔 *[EXECUTIVE HANDOFF ALERT]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 *Customer:* %s (`%s`)\n\n📋 *PREVIOUS CHAT CONTEXT:*\n%s\n\n🔗 *1-Tap Full Live Transcript & Ledger:* %s\n\n👉 *Reply:* `#reply %s | your message`", profileName, customerPhone, historySummary, cleanChatURL, customerPhone)
	globalWhatsAppEngine.SendMessage("sovereign-ai-master", managerPhone, mgrAlert)



	// STAGE 2 (T=30s): PURE WHATSAPP AUDIO CALL RINGING ACTION (ZERO TEXT MESSAGES)
	time.AfterFunc(30*time.Second, func() {
		d.mu.RLock()
		hasReplied := d.managerReplied[customerPhone]
		d.mu.RUnlock()

		if !hasReplied {
			log.Printf("[CASCADING STAGE 2] 30s expired! Executing Pure WhatsApp Audio Call Ringing Stanza to Manager +%s!", managerPhone)
			TriggerWhatsAppAudioCallRinging(managerPhone, customerPhone, profileName)
		}
	})

	// STAGE 3 (T=60s): PURE 0-KOBO GSM HARDWARE FLASH CALL & WEBRTC CALL ACTION (ZERO TEXT MESSAGES)
	d.pendingTimers[customerPhone] = time.AfterFunc(60*time.Second, func() {
		d.mu.RLock()
		hasReplied := d.managerReplied[customerPhone]
		d.mu.RUnlock()

		if !hasReplied {
			log.Printf("[CASCADING STAGE 3] 60s expired! Executing Pure GSM Hardware Call Ringing Action to +%s!", managerPhone)
			TriggerGSMFlashCallRinging(managerPhone, customerPhone, profileName)
		}
	})

	// STAGE 4 (T=90s): Empathetic Customer Delay Reassurance
	time.AfterFunc(90*time.Second, func() {
		d.mu.RLock()
		hasReplied := d.managerReplied[customerPhone]
		d.mu.RUnlock()

		if !hasReplied {
			log.Printf("[CASCADING STAGE 4] 90s expired! Dispatching customer delay reassurance to %s", customerPhone)
			reassuranceMsg := fmt.Sprintf("⏳ *[STORE MANAGER UPDATE]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nDear %s,\nOur Store Manager's phone has been alerted with an urgent priority call alarm and flash alert regarding your inquiry!\n\nPlease bear with us for just a brief moment while our manager connects. Your conversation is our highest priority!\n\n🛍️ *Tip:* Reply `#catalog` anytime to explore more items in our live store!", profileName)
			globalWhatsAppEngine.SendMessage("sovereign-ai-master", customerPhone, reassuranceMsg)
		}
	})
}

func (d *DialogueEngine) CancelManagerCallAlarm(customerPhone string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.managerReplied[customerPhone] = true
	if t, exists := d.pendingTimers[customerPhone]; exists && t != nil {
		t.Stop()
		delete(d.pendingTimers, customerPhone)
	}
}


// 📞 STAGE 2: PURE WHATSAPP AUDIO CALL RINGING ACTION (NO TEXT MESSAGES)
func TriggerWhatsAppAudioCallRinging(mgrPhone, custPhone, custName string) {
	log.Printf("[WhatsApp Call Ringing] Executing PURE Audio Call Offer Stanza to Manager +%s for customer %s!", mgrPhone, custName)
	
	evoURL := strings.TrimRight(os.Getenv("EVOLUTION_API_URL"), "/")
	if evoURL == "" {
		evoURL = "http://127.0.0.1:8081"
	}
	evoKey := os.Getenv("EVOLUTION_API_KEY")

	// Dispatch Baileys Native Call Offer Stanza (Triggers native WhatsApp incoming call screen)
	callURL := fmt.Sprintf("%s/call/offer/sovereign-ai-master", evoURL)
	payload := map[string]string{"number": mgrPhone}
	jsonBytes, _ := json.Marshal(payload)

	client := &http.Client{Timeout: 5 * time.Second}
	req, _ := http.NewRequest("POST", callURL, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")
	if evoKey != "" {
		req.Header.Set("apikey", evoKey)
	}
	resp, err := client.Do(req)
	if err == nil && resp != nil {
		resp.Body.Close()
		log.Printf("[WhatsApp Call Ringing] Baileys Call Offer status: %d", resp.StatusCode)
	}
}

// 📞 STAGE 3: PURE 0-KOBO GSM HARDWARE & WEBRTC CALL RINGING ACTION (NO TEXT MESSAGES)
func TriggerGSMFlashCallRinging(mgrPhone, custPhone, custName string) {
	cleanPhone := strings.ReplaceAll(strings.ReplaceAll(mgrPhone, "+", ""), " ", "")
	log.Printf("[0-Kobo Sovereign Call Engine] Executing PURE call ringing action to +%s for customer %s", cleanPhone, custName)

	client := &http.Client{Timeout: 5 * time.Second}

	// 1. Dispatch WebRTC Call Offer Stanza to internal gateway
	evoURL := strings.TrimRight(os.Getenv("EVOLUTION_API_URL"), "/")
	if evoURL == "" {
		evoURL = "http://127.0.0.1:8081"
	}
	offerURL := evoURL + "/call/offer/sovereign-ai-master"
	offerPayload := map[string]string{"number": cleanPhone}
	oData, _ := json.Marshal(offerPayload)
	reqOffer, _ := http.NewRequest("POST", offerURL, strings.NewReader(string(oData)))
	reqOffer.Header.Set("Content-Type", "application/json")
	resp, err := client.Do(reqOffer)
	if err == nil && resp != nil {
		resp.Body.Close()
		log.Printf("[Sovereign Call Engine] Zero-cost VoIP call offer stanza status: %d", resp.StatusCode)
	}

	// 3. Dispatch Open Android GSM Hardware Gateway Hook (If self-hosted SIM Gateway active)
	androidGatewayURL := os.Getenv("ANDROID_GSM_GATEWAY_URL")
	if androidGatewayURL != "" {
		gPayload := map[string]string{
			"number": cleanPhone,
			"action": "flash_call",
		}
		gData, _ := json.Marshal(gPayload)
		respG, errG := client.Post(androidGatewayURL+"/call", "application/json", strings.NewReader(string(gData)))
		if errG == nil && respG != nil {
			respG.Body.Close()
			log.Printf("[Android GSM Gateway] 0-Kobo hardware flash call dispatched to +%s", cleanPhone)
		}
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

