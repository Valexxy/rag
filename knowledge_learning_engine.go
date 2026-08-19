package main

import (
	"bytes"
	"fmt"
	"log"
	"net/http"
	"strings"
	"sync"
	"time"
)

type KnowledgeFact struct {
	ID        string    `json:"id"`
	Category  string    `json:"category"`
	Question  string    `json:"question"`
	Answer    string    `json:"answer"`
	Source    string    `json:"source"`
	CreatedAt time.Time `json:"created_at"`
}

type AutonomousKnowledgeEngine struct {
	mu             sync.RWMutex
	tenantFacts    map[string][]KnowledgeFact
	customerMemory map[string]map[string]string // phone -> key -> value
}

var globalKnowledgeEngine = &AutonomousKnowledgeEngine{
	tenantFacts:    make(map[string][]KnowledgeFact),
	customerMemory: make(map[string]map[string]string),
}

// LearnFromManagerReply automatically learns new QA pairs from Store Manager responses
func (k *AutonomousKnowledgeEngine) LearnFromManagerReply(merchantID, customerQuery, managerReply string) {
	k.mu.Lock()
	defer k.mu.Unlock()

	cleanQ := strings.TrimSpace(customerQuery)
	cleanA := strings.TrimSpace(managerReply)

	if cleanQ == "" || cleanA == "" {
		return
	}

	fact := KnowledgeFact{
		ID:        fmt.Sprintf("fact_%d", time.Now().UnixNano()),
		Category:  "MANAGER_LEARNED",
		Question:  cleanQ,
		Answer:    cleanA,
		Source:    "STORE_MANAGER_REPLY",
		CreatedAt: time.Now().UTC(),
	}

	k.tenantFacts[merchantID] = append(k.tenantFacts[merchantID], fact)
	log.Printf("[Self-Learning Engine] Learned new QA pair for merchant %s: Question: '%s' | Learned Answer: '%s'", merchantID, cleanQ, cleanA)

	// Asynchronously persist to Supabase tenant knowledge base table
	go func() {
		if supabaseURL != "" && supabaseKey != "" {
			payload := fmt.Sprintf(`{"merchant_id":"%s","category":"MANAGER_LEARNED","question":"%s","answer":"%s"}`, merchantID, cleanQ, cleanA)
			MakeSupabaseRPCRequest("tenant_knowledge_base", payload)
		}
	}()
}

// QueryKnowledgeBase queries the dynamically growing knowledge base (0 hardcoding)
func (k *AutonomousKnowledgeEngine) QueryKnowledgeBase(merchantID, query string) (string, bool) {
	k.mu.RLock()
	defer k.mu.RUnlock()

	lowerQ := strings.ToLower(strings.TrimSpace(query))
	facts, exists := k.tenantFacts[merchantID]
	if !exists || len(facts) == 0 {
		return "", false
	}

	// Search learned facts using keyword matching
	for i := len(facts) - 1; i >= 0; i-- {
		fact := facts[i]
		lowerLearnedQ := strings.ToLower(fact.Question)

		// Check for high semantic overlap
		if strings.Contains(lowerQ, lowerLearnedQ) || strings.Contains(lowerLearnedQ, lowerQ) {
			log.Printf("[Self-Learning Engine] Knowledge Base Hit! Matched Learned Fact: '%s' -> '%s'", fact.Question, fact.Answer)
			return fact.Answer, true
		}

		// Check key term matching
		words := strings.Fields(lowerQ)
		matchCount := 0
		for _, w := range words {
			if len(w) > 3 && strings.Contains(lowerLearnedQ, w) {
				matchCount++
			}
		}
		if len(words) > 0 && float64(matchCount)/float64(len(words)) >= 0.6 {
			log.Printf("[Self-Learning Engine] High-Relevance Knowledge Base Hit for '%s'", query)
			return fact.Answer, true
		}
	}

	return "", false
}

// LearnCustomerPreference records dynamic customer facts (location, delivery preference, orders)
func (k *AutonomousKnowledgeEngine) LearnCustomerPreference(phone, key, value string) {
	k.mu.Lock()
	defer k.mu.Unlock()

	if _, exists := k.customerMemory[phone]; !exists {
		k.customerMemory[phone] = make(map[string]string)
	}

	k.customerMemory[phone][key] = value
	log.Printf("[Self-Learning Engine] Dynamic Memory Updated for %s: %s = '%s'", phone, key, value)
}

// GetCustomerPreference retrieves dynamic customer memory
func (k *AutonomousKnowledgeEngine) GetCustomerPreference(phone, key string) string {
	k.mu.RLock()
	defer k.mu.RUnlock()

	if mem, exists := k.customerMemory[phone]; exists {
		return mem[key]
	}
	return ""
}

// GetDynamicStoreCatalog generates a live, 100% non-hardcoded catalog overview from inventory
func (k *AutonomousKnowledgeEngine) GetDynamicStoreCatalog(businessName string, custLoc CustomerLocation) string {
	locTag := ""
	if custLoc.City != "" {
		if custLoc.State != "" {
			locTag = fmt.Sprintf("📍 *[%s, %s State]*", custLoc.City, custLoc.State)
		} else {
			locTag = fmt.Sprintf("📍 *[%s]*", custLoc.City)
		}
	}

	// Dynamically build product list from storeCatalog slice (pulled live from database/memory)
	var sb strings.Builder
	sb.WriteString(fmt.Sprintf("🛍️ *[LIVE PRODUCT CATALOG — %s]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n%s\n\n", businessName, locTag))

	for i, item := range storeCatalog {
		sb.WriteString(fmt.Sprintf("%d️⃣ *%s*\n    🏷️ Price: ₦%.2f\n    ⚡ Specs: %s\n\n", i+1, item.Name, item.Price, item.Description))
	}

	sb.WriteString("Reply `#buy <id>` (e.g. `#buy 2`) to order any item immediately!")
	return sb.String()
}

func MakeSupabaseRPCRequest(table, jsonPayload string) {
	if supabaseURL == "" || supabaseKey == "" {
		return
	}

	url := fmt.Sprintf("%s/rest/v1/%s", strings.TrimRight(supabaseURL, "/"), table)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer([]byte(jsonPayload)))
	if err != nil {
		return
	}

	req.Header.Set("Content-Type", "application/json")
	req.Header.Set("apikey", supabaseKey)
	req.Header.Set("Authorization", "Bearer "+supabaseKey)
	req.Header.Set("Prefer", "return=minimal")

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err == nil && resp != nil {
		resp.Body.Close()
	}
}

