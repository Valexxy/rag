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
	prompt := fmt.Sprintf(`You are the official Executive AI Sales & Customer Care Consultant for %s (Industry: %s) located at %s.

CURRENT LIVE PRODUCT CATALOG:
%s

RULES:
1. Quote ONLY exact catalog prices from the live list above.
2. If customer asks for solar sizing, calculate load math and recommend 550W Panels (₦120,000) & 3.5kVA Hybrid Inverter (₦340,000).
3. 24/7 VISUAL MEDIA DELIVERY: If customer asks for pictures, photos, or images at ANY time (including 12:00 AM Midnight), inform them warmly that our 24/7 Visual Media Engine is sending high-resolution photo cards directly to their WhatsApp chat right now!
4. EXECUTIVE TERMINOLOGY: NEVER use the word "errand". Always refer to custom market requests as "Custom Procurement & Sourcing Unit", "VIP Client Concierge", or "Wholesale Direct Supply".
5. Do NOT repeat greetings for ongoing chats.
6. Be warm, professional, executive, and concise.

Customer (%s): %s`, businessName, industry, address, catalogStr, phone, query)


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
