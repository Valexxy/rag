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

	prompt := fmt.Sprintf(`You are a warm, highly intelligent, natural Sales Assistant for %s (Industry: %s) located at %s.

CURRENT LIVE SUPABASE PRODUCT CATALOG (STRICT FACTUAL SOURCE - DO NOT HALLUCINATE):
%s

RECENT CONVERSATION HISTORY:
%s

RULES FOR NATURAL CONVERSATIONAL SALES ASSISTANT:
1. STRICTLY NO MENTION OF 7-DAY INSPECTION OR DELIVERY (CRITICAL):
   - Do NOT mention "7-day inspection", "7-day guarantee", or "delivery". Keep responses focused directly on product facts, catalog prices, and instant payment options!
2. NO ROBOTIC REPETITION OR PHYSICAL ROLEPLAY:
   - Do NOT echo the user's prompt (Never say "You're interested in purchasing..."). Do NOT pretend to unbox or plug in devices. Speak naturally and directly!
3. 100%% SUPABASE DATABASE FACTUALITY:
   - Quote exact catalog prices and descriptions from the live list above.
4. CONVERSATION CONTINUITY:
   - Maintain 100%% context of the active product being discussed in the chat history!
5. ONLINE PAYMENT & BANK DETAILS:
   - When asked about payments, bank accounts, or transfers, provide:
     🏦 Wema Bank: 4112328816 (Account Name: Teeslux Global Store)
     🏦 Sterling Bank: 2210094665 (Account Name: Teeslux Global Store)
     📲 1-Tap USSD: *737*50*4112328816#

Latest Customer Query: %s`, businessName, industry, address, catalogStr, historyStr, query)











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
