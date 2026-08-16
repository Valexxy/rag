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
		evoURL = "http://127.0.0.1:8081"
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
	if err == nil && (resp.StatusCode == 200 || resp.StatusCode == 201) {
		resp.Body.Close()
		log.Printf("[WhatsApp Engine] Sent zero-cost message to %s via Evolution API", cleanPhone)
		return
	}
	if resp != nil {
		resp.Body.Close()
	}

	// Automatic Failover to Meta Cloud Graph API
	log.Printf("[WhatsApp Engine] Evolution API unavailable (503/Timeout). Hot-swapping to Meta Cloud API for %s", cleanPhone)
	w.SendMetaCloudMessage(cleanPhone, text)
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
		evoURL = "http://127.0.0.1:8081"
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
	if err == nil && (resp.StatusCode == 200 || resp.StatusCode == 201) {
		resp.Body.Close()
		log.Printf("[WhatsApp Engine] Sent zero-cost media image card to %s", cleanPhone)
		return
	}
	if resp != nil {
		resp.Body.Close()
	}

	// Automatic Failover to Meta Cloud Graph API with text caption
	w.SendMetaCloudMessage(cleanPhone, caption+"\n🖼️ Image: "+imageURL)
}


func (w *WhatsAppEngine) SendMetaCloudMessage(senderPhone, text string) {
	phoneID := os.Getenv("META_PHONE_NUMBER_ID")
	if phoneID == "" {
		phoneID = "1237917316076300"
	}
	token := os.Getenv("META_WHATSAPP_TOKEN")
	if token == "" {
		token = "EAAMgsrreXPYBSLt3Lr7GH3kllx4WKOkV0SvtTxzqVZAEQM5rHVlzgXarNNv9sHuhxJe5ZBpyngRWuTgVGZCkAtzA6yJxc4YzuyY1alLa6OolrBmUOPHNp4vCHCPDgkSj069HzZCFK3nCTwIMQ3GuyA0fTXj03yDGuPGnBLeQLlY4RwvcsShKJ92NNTlFrxD7VONkmJgVYYnYfMLzvbm304wwCZB3qr6hv8Dn72zNUtorAWGlEQUiAdGVoZCjVzEFVUXRh36ZAs2ZBikzKxF12NLSJwZDZD"
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
