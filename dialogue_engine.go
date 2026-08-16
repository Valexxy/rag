package main

import (
	"fmt"
	"strconv"
	"strings"
	"sync"
	"time"
)

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
}

var globalDialogueEngine = &DialogueEngine{
	states:        make(map[string]string),
	memoryThreads: make(map[string][]ChatTurn),
	lastActivity:  make(map[string]time.Time),
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
	d.SetState(phone, "IDLE")
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
		managerNotice := fmt.Sprintf("👔 *[EXECUTIVE HANDOFF ALERT]*\nCustomer `%s` requested human manager support via #manager command!", senderPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", managerPhone, managerNotice)
		return true, "👔 *[Connected to Human Manager]*\nThe AI Bot has disengaged. Our Store Manager (2348072015725) has been notified to connect with you directly!"

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

		replyPayload := fmt.Sprintf("💬 *[Store Manager]:* %s\n\n📞 *Call Manager:* tel:+%s\n💬 *Chat Manager:* https://wa.me/%s", msgText, senderPhone, senderPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", targetPhone, replyPayload)
		return true, fmt.Sprintf("✅ Message delivered to customer `%s`.", targetPhone)

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

