package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
	"time"
)


// AIEngine manages multi-provider AI model failover & key rotation
type AIEngine struct {
	mu           sync.RWMutex
	groqKeys     []string
	cerebrasKeys []string
	currentIdx   int
}

var globalAIEngine = &AIEngine{
	groqKeys: []string{
		"gsk_free_groq_key_1",
		"gsk_free_groq_key_2",
	},
	cerebrasKeys: []string{
		"csk_free_cerebras_key_1",
	},
}

func (ai *AIEngine) GenerateReply(query, phone, businessName, address, industry, catalogStr string, history []ChatTurn) string {
	var histLines []string
	for _, turn := range history {
		if turn.Role == "user" {
			histLines = append(histLines, fmt.Sprintf("Customer: %s", turn.Content))
		} else {
			histLines = append(histLines, fmt.Sprintf("Assistant: %s", turn.Content))
		}
	}
	historyStr := strings.Join(histLines, "\n")
	if historyStr == "" {
		historyStr = "None (First message)"
	}

	txSummaryStr := globalPaymentLedger.GetCustomerLedgerSummary(historyStr)

	prompt := fmt.Sprintf(`You are a polite, highly intelligent, elite E-Commerce Sales Specialist for %s (Industry: %s) located at %s.

CURRENT LIVE SUPABASE PRODUCT CATALOG (STRICT FACTUAL SOURCE - DO NOT HALLUCINATE):
%s

LIFETIME CUSTOMER TRANSACTION LEDGER (PERMANENT UNERASABLE MEMORY):
%s

PERMANENT CONVERSATION HISTORY:
%s

RULES FOR REAL E-COMMERCE CONCIERGE ASSISTANT:
1. PERMANENT LIFETIME MEMORY & TRANSACTION AWARENESS (UNERASABLE):
   - You have 100%% unerasable memory of this customer's past purchases, payments, and conversation history even if they cleared their phone chat. Reference past items and payment status naturally!
2. AUTOMATIC CROSS-SELL / UP-SELL PROTOCOL:
   - At the end of every sale or product inquiry, politely suggest a complementary catalog item (e.g., recommend 550W Monocrystalline Solar Panel or 3.5kVA Hybrid Inverter if they bought a Solar Power Bank).
3. AUTOMATIC HUMAN ESCALATION PROTOCOL:
   - Whenever you are confused, receive an unknown request, or if the customer asks for a human/manager/agent, state warmly: "I have notified our Store Manager (2348072015725) with your request!"
4. CLEAN E-COMMERCE PURCHASE CONFIRMATION:
   - Never ask nosey personal questions. Thank them for their patronage and suggest complementary items!
5. 100%% SUPABASE DATABASE FACTUALITY:
   - Quote exact catalog prices from the live catalog list above.
6. ONLINE PAYMENT & BANK DETAILS:
   - When asked about payments, bank accounts, or transfers, provide:
     🏦 Wema Bank: 4112328816 (Account Name: Teeslux Global Store)
     🏦 Sterling Bank: 2210094665 (Account Name: Teeslux Global Store)
     📲 1-Tap USSD: *737*50*4112328816#
7. SHORT & CRISP RESPONSES ONLY (NO LONG SELF-JUSTIFYING ESSAYS):
   - Keep all responses short, professional, and focused strictly on products, prices, and orders (under 3 sentences). Never write long self-justifying essays or apologize repeatedly!
8. NAIJA MULTI-LINGUAL & DIALECT INTELLIGENCE (EFFORTLESS PIDGIN, YORUBA, HAUSA, IGBO):
   - You natively understand and reply in authentic Nigerian Pidgin ("How much be solar panel abeg?"), Yoruba ("E kaaro, elo ni power bank?"), Hausa ("Sannu, nawa ne solar panel?"), Igbo ("Kedu kene power bank?"), and Nigerian English. Match the customer's language and dialect with natural Nigerian warmth and politeness! Always use Naira (₦) currency formatting.

Latest Customer Query: %s`, businessName, industry, address, catalogStr, txSummaryStr, historyStr, query)














	// Try Groq -> Cerebras -> Fallback
	reply := ai.callGroq(prompt)
	if reply != "" {
		return reply
	}

	reply = ai.callCerebras(prompt)
	if reply != "" {
		return reply
	}

	return fmt.Sprintf("Welcome to %s! We offer Tier-1 550W Solar Panels (₦120,000) and 3.5kVA Hybrid Inverter Systems (₦340,000). How may I assist your power needs today?", businessName)
}

func (ai *AIEngine) callGroq(prompt string) string {
	apiKey := os.Getenv("GROQ_API_KEY")
	if apiKey == "" {
		return ""
	}

	url := "https://api.groq.com/openai/v1/chat/completions"
	payload := map[string]interface{}{
		"model": "llama-3.3-70b-versatile",
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
		"max_tokens": 400,
	}

	jsonBytes, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		log.Printf("[AI Engine Error] Groq call failed: %v", err)
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return ""
	}

	body, _ := io.ReadAll(resp.Body)
	var res map[string]interface{}
	json.Unmarshal(body, &res)

	if choices, ok := res["choices"].([]interface{}); ok && len(choices) > 0 {
		choice := choices[0].(map[string]interface{})
		message := choice["message"].(map[string]interface{})
		return message["content"].(string)
	}

	return ""
}

func (ai *AIEngine) callCerebras(prompt string) string {
	apiKey := os.Getenv("CEREBRAS_API_KEY")
	if apiKey == "" {
		return ""
	}

	url := "https://api.cerebras.ai/v1/chat/completions"
	payload := map[string]interface{}{
		"model": "llama-3.3-70b",
		"messages": []map[string]string{
			{"role": "user", "content": prompt},
		},
		"max_tokens": 400,
	}

	jsonBytes, _ := json.Marshal(payload)
	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Authorization", "Bearer "+apiKey)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 4 * time.Second}
	resp, err := client.Do(req)
	if err != nil {
		return ""
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return ""
	}

	body, _ := io.ReadAll(resp.Body)
	var res map[string]interface{}
	json.Unmarshal(body, &res)

	if choices, ok := res["choices"].([]interface{}); ok && len(choices) > 0 {
		choice := choices[0].(map[string]interface{})
		message := choice["message"].(map[string]interface{})
		return message["content"].(string)
	}

	return ""
}
