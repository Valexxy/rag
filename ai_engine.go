package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
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

func (ai *AIEngine) GenerateReply(query, phone, businessName, address, industry, catalogStr string) string {
	prompt := fmt.Sprintf(`You are the official Customer Care & Sales Assistant for %s (Industry: %s) located at %s.

CURRENT LIVE PRODUCT CATALOG:
%s

RULES:
1. Quote ONLY exact catalog prices from the live list above.
2. Be natural, warm, conversational, and genuinely helpful. Answer the customer's questions directly according to the direction of the chat.
3. NEVER invent fake names (e.g. do NOT say "Mr. Emeka"). Use the customer's real name if provided, otherwise address them naturally without forcing a name.
4. Do NOT assume or state the customer's city, location, or weather unless the customer explicitly tells you where they are located.
5. Do NOT use forced corporate jargon like "procurement" or "VIP Concierge" unless the customer explicitly asks for corporate wholesale procurement.
6. When asked for photos, state warmly that product photos are available for all items.
7. Keep responses concise, helpful, and natural.

Customer Query: %s`, businessName, industry, address, catalogStr, query)





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
