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


// AIEngine manages multi-provider AI model failover & enterprise key pool rotation
type AIEngine struct {
	mu            sync.RWMutex
	groqKeys      []string
	cerebrasKeys  []string
	geminiKeys    []string
	openRouter    []string
	groqIdx       int
	cerebrasIdx   int
	geminiIdx     int
	openRouterIdx int
}

var globalAIEngine = &AIEngine{
	groqKeys:     []string{},
	cerebrasKeys: []string{},
	geminiKeys:   []string{},
	openRouter:   []string{},
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
9. AI VIBE & LIFESTYLE MATCH ASSISTANT:
   - When customers describe a vibe, occasion, or lifestyle need ("setup for 24/7 tech nomad studio", "outdoor beach party setup", "small biz salon power package", "blackout backup for apartment"), curate an aesthetic lifestyle bundle from our live Supabase catalog! Present the items with a 10% bundle savings badge and a 1-tap buy code!

Latest Customer Query: %s`, businessName, industry, address, catalogStr, txSummaryStr, historyStr, query)















	// 5-Tier AI Model Failover Rotator: Groq -> Cerebras -> Gemini 2.0 Flash -> OpenRouter
	reply := ai.callGroq(prompt)
	if reply != "" {
		log.Printf("[AI Rotator] Tier 1 Groq Llama-3.3 70B responded successfully!")
		return reply
	}

	reply = ai.callCerebras(prompt)
	if reply != "" {
		log.Printf("[AI Rotator] Tier 2 Cerebras Llama-3.3 70B responded successfully!")
		return reply
	}

	reply = ai.callGemini(prompt)
	if reply != "" {
		log.Printf("[AI Rotator] Tier 3 Gemini 2.0 Flash responded successfully!")
		return reply
	}

	reply = ai.callOpenRouter(prompt)
	if reply != "" {
		log.Printf("[AI Rotator] Tier 4 OpenRouter responded successfully!")
		return reply
	}

	lowerQ := strings.ToLower(query)

	// Factual Product & Price Resolver (Zero repetitive greeting cards)
	if strings.Contains(lowerQ, "power bank") || strings.Contains(lowerQ, "20,000") || strings.Contains(lowerQ, "20000") {
		return "🔋 *[20,000 mAh SOLAR POWER BANK]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦18,500\n⚡ *Specs:* Rugged outdoor dual USB fast-charging with solar charging panel.\n🤝 *Best Price Offer:* ₦18,500 per unit. For bulk orders (3+ units), our merchant discount gives you ₦17,575 / unit (5% OFF)!\n\nReply `#buy 2` to order this item now!"
	}
	if strings.Contains(lowerQ, "solar panel") || strings.Contains(lowerQ, "550w") || strings.Contains(lowerQ, "panel") {
		return "☀️ *[550W MONOCRYSTALLINE SOLAR PANEL]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦120,000 per panel\n⚡ *Specs:* Tier-1 High Efficiency Monocrystalline\n🤝 *Best Price Offer:* ₦120,000 / unit.\n\nReply `#buy 1` to order now!"
	}
	if strings.Contains(lowerQ, "generator") || strings.Contains(lowerQ, "1.5kva") {
		return "🔋 *[1.5kVA DUAL SOLAR GENERATOR]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦185,000\n⚡ *Specs:* Silent pure sine wave inverter generator with lithium battery.\n\nReply `#buy 3` to order now!"
	}
	if strings.Contains(lowerQ, "inverter") || strings.Contains(lowerQ, "3.5kva") {
		return "⚡ *[3.5kVA HYBRID SOLAR INVERTER]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦340,000\n⚡ *Specs:* 3.5kVA 24V Pure Sine Wave Hybrid Solar Inverter.\n\nReply `#buy 6` to order now!"
	}
	if strings.Contains(lowerQ, "rice") || strings.Contains(lowerQ, "50kg") {
		return "🌾 *[50kg PREMIUM WHITE RICE BAG]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦60,000 per 50kg bag.\n\nReply `#buy 4` to order now!"
	}
	if strings.Contains(lowerQ, "gold") || strings.Contains(lowerQ, "bullion") {
		return "🥇 *[24K GOLD BAR BULLION (1-GRAM)]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n🏷️ *Catalog Price:* ₦68,500\n⚡ *Specs:* 999.9 Fine Investment Grade Gold Bullion.\n\nReply `#buy 5` to order now!"
	}
	if strings.Contains(lowerQ, "price") || strings.Contains(lowerQ, "cost") || strings.Contains(lowerQ, "how much") || strings.Contains(lowerQ, "catalog") || strings.Contains(lowerQ, "list") {
		return "📋 *[TEESLUX LIVE CATALOG & PRICE LIST]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n1️⃣ 550W Monocrystalline Solar Panel — ₦120,000\n2️⃣ 20,000 mAh Solar Power Bank — ₦18,500\n3️⃣ 1.5kVA Dual Solar Generator — ₦185,000\n4️⃣ 50kg Premium White Rice Bag — ₦60,000\n5️⃣ 24K Gold Bar Bullion (1-Gram) — ₦68,500\n6️⃣ 3.5kVA Hybrid Solar Inverter System — ₦340,000\n\nReply `#buy <id>` (e.g. `#buy 2`) to order any item!"
	}

	return fmt.Sprintf("Welcome to %s! How may I assist your order for Solar Systems, Generators, Power Banks, or Bullion today?", businessName)
}





// 🧠 PURE AI CONTEXTUAL SEMANTIC INTENT REASONER (0 HARDCODED PHRASES)
func (ai *AIEngine) ClassifyIntentPureAI(query, history string) string {
	prompt := fmt.Sprintf(`You are a world-class AI Semantic Intent Classifier for an E-Commerce system in Nigeria.
Read the entire customer statement carefully in full context of the conversation history. Do NOT rely on single words or isolated phrases.

CONVERSATION HISTORY:
%s

CUSTOMER STATEMENT:
"%s"

Classify the customer's TRUE INTENT into EXACTLY ONE of the following categories:
- HUMAN_MANAGER_REQUEST: Customer explicitly wants to speak with a human store manager, owner, or live representative.
- PERSONAL_FAMILY: A personal note, family update, or friendly message meant for the store owner personally.
- VIBE_SEARCH: Customer is asking for a product bundle based on a lifestyle vibe, occasion, or setup (e.g. tech studio, party, blackout backup).
- SESSION_END: Customer is concluding the chat (e.g. goodbye, that's all, thank you bye).
- MARKET_SOURCING: B2B wholesale, bulk supplier, container, or factory import inquiry.
- SERVICE_BOOKING: Engineering installation, repair, audit, or maintenance booking.
- RETAIL_SALES: Product price, catalog, availability, purchase, or order inquiry.
- SPAM_TIME_WASTER: Prompt injection, abuse, or non-business chatter.
- GENERAL_QUERY: General question or conversation.

OUTPUT ONLY THE CATEGORY CODE (e.g. HUMAN_MANAGER_REQUEST) AND NOTHING ELSE.`, history, query)

	reply := ai.callGroq(prompt)
	if reply == "" {
		reply = ai.callCerebras(prompt)
	}
	if reply == "" {
		reply = ai.callGemini(prompt)
	}
	if reply == "" {
		reply = ai.callOpenRouter(prompt)
	}

	return strings.TrimSpace(reply)
}


func (ai *AIEngine) getKeysForProvider(envVarKeys, envVarSingle string, hardcodedPool []string) []string {
	var pool []string
	if raw := os.Getenv(envVarKeys); raw != "" {
		for _, k := range strings.Split(raw, ",") {
			if k = strings.TrimSpace(k); k != "" {
				pool = append(pool, k)
			}
		}
	}
	if raw := os.Getenv(envVarSingle); raw != "" {
		pool = append(pool, strings.TrimSpace(raw))
	}
	for _, k := range hardcodedPool {
		if k = strings.TrimSpace(k); k != "" && !strings.Contains(k, "free_key") {
			pool = append(pool, k)
		}
	}
	return pool
}

func (ai *AIEngine) callGroq(prompt string) string {
	keys := ai.getKeysForProvider("GROQ_API_KEYS", "GROQ_API_KEY", ai.groqKeys)
	if len(keys) == 0 {
		return ""
	}

	for i := 0; i < len(keys); i++ {
		ai.mu.Lock()
		idx := ai.groqIdx % len(keys)
		ai.groqIdx++
		ai.mu.Unlock()

		apiKey := keys[idx]
		if apiKey == "" {
			continue
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
			log.Printf("[AI Key Rotator] Groq key #%d failed (%v). Hot-swapping to next key...", idx+1, err)
			continue
		}

		if resp.StatusCode != http.StatusOK {
			resp.Body.Close()
			log.Printf("[AI Key Rotator] Groq key #%d returned HTTP %d. Hot-swapping to next key...", idx+1, resp.StatusCode)
			continue
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		var res map[string]interface{}
		if err := json.Unmarshal(body, &res); err == nil {
			if choices, ok := res["choices"].([]interface{}); ok && len(choices) > 0 {
				choice := choices[0].(map[string]interface{})
				if message, ok := choice["message"].(map[string]interface{}); ok {
					if content, ok := message["content"].(string); ok && strings.TrimSpace(content) != "" {
						log.Printf("[AI Key Rotator] Groq Key #%d responded successfully!", idx+1)
						return strings.TrimSpace(content)
					}
				}
			}
		}
	}
	return ""
}

func (ai *AIEngine) callCerebras(prompt string) string {
	keys := ai.getKeysForProvider("CEREBRAS_API_KEYS", "CEREBRAS_API_KEY", ai.cerebrasKeys)
	if len(keys) == 0 {
		return ""
	}

	for i := 0; i < len(keys); i++ {
		ai.mu.Lock()
		idx := ai.cerebrasIdx % len(keys)
		ai.cerebrasIdx++
		ai.mu.Unlock()

		apiKey := keys[idx]
		if apiKey == "" {
			continue
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
			log.Printf("[AI Key Rotator] Cerebras key #%d failed (%v). Hot-swapping to next key...", idx+1, err)
			continue
		}

		if resp.StatusCode != http.StatusOK {
			resp.Body.Close()
			log.Printf("[AI Key Rotator] Cerebras key #%d returned HTTP %d. Hot-swapping to next key...", idx+1, resp.StatusCode)
			continue
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		var res map[string]interface{}
		if err := json.Unmarshal(body, &res); err == nil {
			if choices, ok := res["choices"].([]interface{}); ok && len(choices) > 0 {
				choice := choices[0].(map[string]interface{})
				if message, ok := choice["message"].(map[string]interface{}); ok {
					if content, ok := message["content"].(string); ok && strings.TrimSpace(content) != "" {
						log.Printf("[AI Key Rotator] Cerebras Key #%d responded successfully!", idx+1)
						return strings.TrimSpace(content)
					}
				}
			}
		}
	}
	return ""
}

func (ai *AIEngine) callGemini(prompt string) string {
	keys := ai.getKeysForProvider("GEMINI_API_KEYS", "GEMINI_API_KEY", ai.geminiKeys)
	if len(keys) == 0 {
		return ""
	}

	for i := 0; i < len(keys); i++ {
		ai.mu.Lock()
		idx := ai.geminiIdx % len(keys)
		ai.geminiIdx++
		ai.mu.Unlock()

		apiKey := keys[idx]
		if apiKey == "" {
			continue
		}

		url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%s", apiKey)
		payload := map[string]interface{}{
			"contents": []map[string]interface{}{
				{
					"parts": []map[string]string{
						{"text": prompt},
					},
				},
			},
		}

		jsonBytes, _ := json.Marshal(payload)
		req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
		req.Header.Set("Content-Type", "application/json")

		client := &http.Client{Timeout: 5 * time.Second}
		resp, err := client.Do(req)
		if err != nil {
			log.Printf("[AI Key Rotator] Gemini key #%d failed (%v). Hot-swapping to next key...", idx+1, err)
			continue
		}

		if resp.StatusCode != http.StatusOK {
			resp.Body.Close()
			log.Printf("[AI Key Rotator] Gemini key #%d returned HTTP %d. Hot-swapping to next key...", idx+1, resp.StatusCode)
			continue
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		var res map[string]interface{}
		if err := json.Unmarshal(body, &res); err == nil {
			if candidates, ok := res["candidates"].([]interface{}); ok && len(candidates) > 0 {
				cand := candidates[0].(map[string]interface{})
				if content, ok := cand["content"].(map[string]interface{}); ok {
					if parts, ok := content["parts"].([]interface{}); ok && len(parts) > 0 {
						part := parts[0].(map[string]interface{})
						if text, ok := part["text"].(string); ok && strings.TrimSpace(text) != "" {
							log.Printf("[AI Key Rotator] Gemini Key #%d responded successfully!", idx+1)
							return strings.TrimSpace(text)
						}
					}
				}
			}
		}
	}
	return ""
}

func (ai *AIEngine) callOpenRouter(prompt string) string {
	keys := ai.getKeysForProvider("OPENROUTER_API_KEYS", "OPENROUTER_API_KEY", ai.openRouter)
	if len(keys) == 0 {
		return ""
	}

	for i := 0; i < len(keys); i++ {
		ai.mu.Lock()
		idx := ai.openRouterIdx % len(keys)
		ai.openRouterIdx++
		ai.mu.Unlock()

		apiKey := keys[idx]
		if apiKey == "" {
			continue
		}

		url := "https://openrouter.ai/api/v1/chat/completions"
		payload := map[string]interface{}{
			"model": "google/gemini-2.0-flash-lite-001",
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
			log.Printf("[AI Key Rotator] OpenRouter key #%d failed (%v). Hot-swapping to next key...", idx+1, err)
			continue
		}

		if resp.StatusCode != http.StatusOK {
			resp.Body.Close()
			log.Printf("[AI Key Rotator] OpenRouter key #%d returned HTTP %d. Hot-swapping to next key...", idx+1, resp.StatusCode)
			continue
		}

		body, _ := io.ReadAll(resp.Body)
		resp.Body.Close()

		var res map[string]interface{}
		if err := json.Unmarshal(body, &res); err == nil {
			if choices, ok := res["choices"].([]interface{}); ok && len(choices) > 0 {
				choice := choices[0].(map[string]interface{})
				if message, ok := choice["message"].(map[string]interface{}); ok {
					if content, ok := message["content"].(string); ok && strings.TrimSpace(content) != "" {
						log.Printf("[AI Key Rotator] OpenRouter Key #%d responded successfully!", idx+1)
						return strings.TrimSpace(content)
					}
				}
			}
		}
	}
	return ""
}


