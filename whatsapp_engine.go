package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strings"
	"time"
)

type WhatsAppEngine struct{}

var globalWhatsAppEngine = &WhatsAppEngine{}

func (w *WhatsAppEngine) SendMessage(instanceName, phone, text string) {
	cleanPhone := strings.Map(func(r rune) rune {
		if r >= '0' && r <= '9' {
			return r
		}
		return -1
	}, phone)

	if cleanPhone == "" {
		return
	}

	// Send via Open-Source Baileys / Evolution API Gateway (0 Meta Fees)
	evoURL := strings.TrimRight(os.Getenv("EVOLUTION_API_URL"), "/")
	if evoURL == "" {
		evoURL = "https://evolution-api-latest-gxue.onrender.com"
	}
	evoKey := os.Getenv("EVOLUTION_API_KEY")

	url := fmt.Sprintf("%s/message/sendText/%s", evoURL, instanceName)
	payload := map[string]string{
		"number": cleanPhone,
		"text":   strings.TrimSpace(text),
	}
	jsonBytes, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")
	if evoKey != "" {
		req.Header.Set("apikey", evoKey)
	}

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err == nil {
		resp.Body.Close()
		log.Printf("[WhatsApp Engine] Sent zero-cost message to %s via Evolution API", cleanPhone)
	}
}

func (w *WhatsAppEngine) SendMediaImage(instanceName, phone, imageURL, caption string) {
	cleanPhone := strings.Map(func(r rune) rune {
		if r >= '0' && r <= '9' {
			return r
		}
		return -1
	}, phone)

	if cleanPhone == "" || imageURL == "" {
		return
	}

	evoURL := strings.TrimRight(os.Getenv("EVOLUTION_API_URL"), "/")
	if evoURL == "" {
		evoURL = "https://evolution-api-latest-gxue.onrender.com"
	}
	evoKey := os.Getenv("EVOLUTION_API_KEY")

	url := fmt.Sprintf("%s/message/sendMedia/%s", evoURL, instanceName)
	payload := map[string]interface{}{
		"number":    cleanPhone,
		"media":     imageURL,
		"mediatype": "image",
		"caption":   caption,
	}
	jsonBytes, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Content-Type", "application/json")
	if evoKey != "" {
		req.Header.Set("apikey", evoKey)
	}

	client := &http.Client{Timeout: 8 * time.Second}
	resp, err := client.Do(req)
	if err == nil {
		resp.Body.Close()
		log.Printf("[WhatsApp Engine] Sent zero-cost media image card to %s", cleanPhone)
	}
}

func (w *WhatsAppEngine) SendMetaCloudMessage(senderPhone, text string) {
	phoneID := os.Getenv("META_PHONE_NUMBER_ID")
	token := os.Getenv("META_WHATSAPP_TOKEN")
	if phoneID == "" || token == "" {
		w.SendMessage("sovereign-ai-master", senderPhone, text)
		return
	}

	url := fmt.Sprintf("https://graph.facebook.com/v18.0/%s/messages", phoneID)
	payload := map[string]interface{}{
		"messaging_product": "whatsapp",
		"to":                senderPhone,
		"type":              "text",
		"text": map[string]string{
			"body": text,
		},
	}
	jsonBytes, _ := json.Marshal(payload)

	req, _ := http.NewRequest("POST", url, bytes.NewBuffer(jsonBytes))
	req.Header.Set("Authorization", "Bearer "+token)
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 5 * time.Second}
	resp, err := client.Do(req)
	if err == nil {
		resp.Body.Close()
	}
}
