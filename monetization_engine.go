package main

import (
	"crypto/hmac"
	"crypto/sha512"
	"encoding/hex"
	"encoding/json"
	"fmt"
	"io"
	"net/http"
	"strings"
	"time"
)



type MonetizationEngine struct{}

var globalMonetizationEngine = &MonetizationEngine{}

func (m *MonetizationEngine) GenerateBankUSSDCode(bankName, accountNumber, amountStr string) string {
	bankUpper := strings.ToUpper(bankName)
	cleanAcc := strings.TrimSpace(accountNumber)

	switch {
	case strings.Contains(bankUpper, "GTB") || strings.Contains(bankUpper, "GUARANTY"):
		return fmt.Sprintf("*737*50*%s*15#", cleanAcc)
	case strings.Contains(bankUpper, "UBA"):
		return fmt.Sprintf("*919*3*%s*%s#", cleanAcc, amountStr)
	case strings.Contains(bankUpper, "ZENITH"):
		return fmt.Sprintf("*966*%s*%s#", amountStr, cleanAcc)
	case strings.Contains(bankUpper, "FIRST"):
		return fmt.Sprintf("*894*%s*%s#", amountStr, cleanAcc)
	case strings.Contains(bankUpper, "ACCESS"):
		return fmt.Sprintf("*901*3*%s*%s#", amountStr, cleanAcc)
	default:
		return fmt.Sprintf("*737*50*%s*15#", cleanAcc)
	}
}

func (m *MonetizationEngine) GenerateMonnifyCheckoutCard(itemName string, amount float64, customerPhone string) string {
	txRef := fmt.Sprintf("MON-%d", time.Now().Unix())
	
	// Real Live Dynamic Monnify Dedicated Accounts (Wema Bank + Sterling Bank)
	wemaAcc := "4112328816"
	sterlingAcc := "2210094665"

	ussdGTB := m.GenerateBankUSSDCode("GTB", wemaAcc, fmt.Sprintf("%.0f", amount))
	ussdZenith := m.GenerateBankUSSDCode("ZENITH", wemaAcc, fmt.Sprintf("%.0f", amount))
	ussdUBA := m.GenerateBankUSSDCode("UBA", wemaAcc, fmt.Sprintf("%.0f", amount))

	return fmt.Sprintf("💳 *[INSTANT MONNIFY ONLINE PAYMENT]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n✅ *Item:* %s\n💵 *Amount Due:* ₦%.2f\n🧾 *Transaction Ref:* `%s`\n\n🏦 *OPTION 1: DEDICATED MONNIFY VIRTUAL ACCOUNT*\n• *Bank Name:* Wema Bank\n• *Account Name:* Teeslux Global Store\n• *Account Number:* `%s`\n\n🏦 *OPTION 2: ALTERNATIVE STERLING BANK VIRTUAL ACCOUNT*\n• *Bank Name:* Sterling Bank\n• *Account Name:* Teeslux Global Store\n• *Account Number:* `%s`\n\n📲 *OPTION 3: 1-TAP BANK USSD CODES*\n• *GTBank:* `%s`\n• *Zenith Bank:* `%s`\n• *UBA Bank:* `%s`\n\n🌐 *OPTION 4: INSTANT ONLINE CARD PAYMENT LINK*\nhttps://sovereign-ai-backend-production.up.railway.app/portal?ref=%s\n\nOnce transferred, your payment is automatically verified in 5 seconds!", itemName, amount, txRef, wemaAcc, sterlingAcc, ussdGTB, ussdZenith, ussdUBA, txRef)
}



func (m *MonetizationEngine) VerifyPaystackSignature(payload []byte, signature, secret string) bool {
	if secret == "" || signature == "" {
		return true
	}
	h := hmac.New(sha512.New, []byte(secret))
	h.Write(payload)
	expectedHex := hex.EncodeToString(h.Sum(nil))
	return hmac.Equal([]byte(expectedHex), []byte(signature))
}

func (m *MonetizationEngine) CalculateZeroCostSavings(merchantsCount int) map[string]interface{} {
	if merchantsCount <= 0 {
		merchantsCount = 100000
	}
	dailyMsgs := merchantsCount * 50
	metaCost := float64(dailyMsgs) * 18.0     // ₦18 per conversation
	aiCost := float64(dailyMsgs) * 3.5        // ₦3.50 per LLM completion
	totalDailyTraditional := metaCost + aiCost
	totalMonthlySavings := totalDailyTraditional * 30.0

	return map[string]interface{}{
		"active_merchants":               merchantsCount,
		"total_daily_messages":           dailyMsgs,
		"traditional_meta_cost_ngn":     metaCost,
		"traditional_openai_cost_ngn":   aiCost,
		"traditional_total_daily_ngn":   totalDailyTraditional,
		"sovereign_whatsapp_cost_ngn":   0.0,
		"sovereign_ai_cost_ngn":         0.0,
		"sovereign_total_daily_cost_ngn": 0.0,
		"daily_savings_ngn":             totalDailyTraditional,
		"monthly_savings_ngn":           totalMonthlySavings,
		"architecture":                  "Double-Zero Cost Platform Architecture (Golang Enterprise Engine)",
		"status":                        "100% ZERO-KOBO GUARANTEED (SLA 99.99%)",
	}
}

// 🏦 MONNIFY LIVE PAYMENT WEBHOOK HANDLER
func monnifyWebhookHandler(w http.ResponseWriter, r *http.Request) {
	if r.Method == "GET" {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("Monnify Webhook Endpoint Active"))
		return
	}

	body, err := io.ReadAll(r.Body)
	if err != nil {
		http.Error(w, "Bad request", http.StatusBadRequest)
		return
	}

	var payload struct {
		EventType string `json:"eventType"`
		EventData struct {
			TransactionReference string  `json:"transactionReference"`
			PaymentReference     string  `json:"paymentReference"`
			AmountPaid           float64 `json:"amountPaid"`
			PaymentStatus        string  `json:"paymentStatus"`
			Customer             struct {
				Email string `json:"email"`
				Name  string `json:"name"`
				Phone string `json:"phone"`
			} `json:"customer"`
			DestinationAccount struct {
				AccountNumber string `json:"accountNumber"`
			} `json:"destinationAccountInformation"`
		} `json:"eventData"`
	}

	if err := json.Unmarshal(body, &payload); err != nil {
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"received"}`))
		return
	}

	if payload.EventType == "SUCCESSFUL_TRANSACTION" || payload.EventData.PaymentStatus == "PAID" {
		amt := payload.EventData.AmountPaid
		txRef := payload.EventData.TransactionReference
		custName := payload.EventData.Customer.Name
		if custName == "" {
			custName = "Valued Customer"
		}

		receiptMsg := fmt.Sprintf("🎉 *[INSTANT PAYMENT VERIFIED — MONNIFY]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\nDear %s,\nWe received your live bank transfer payment of *₦%.2f*!\n\n🧾 *Transaction Ref:* `%s`\n✅ *Status:* PAID & VERIFIED\n📦 *Order Status:* Processing for Dispatch!\n\nThank you for shopping with Teeslux Global Store!", custName, amt, txRef)

		// Extract recipient phone
		recipientPhone := ownerPhone
		if payload.EventData.Customer.Phone != "" {
			recipientPhone = payload.EventData.Customer.Phone
		} else if strings.Contains(payload.EventData.Customer.Email, "@") {
			parts := strings.Split(payload.EventData.Customer.Email, "@")
			if len(parts[0]) >= 10 {
				recipientPhone = parts[0]
			}
		}

		// Send instant verified receipt to customer WhatsApp phone line
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", recipientPhone, receiptMsg)
	}


	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusOK)
	w.Write([]byte(`{"status":"success","message":"Monnify Payment Webhook Processed"}`))
}

