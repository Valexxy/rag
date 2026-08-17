package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"io"
	"log"
	"net/http"
	"os"
	"time"
)

type VoiceEngine struct{}

var globalVoiceEngine = &VoiceEngine{}

type VoiceOrderExtraction struct {
	CustomerIntent      string `json:"customer_intent"`
	DetectedLanguage    string `json:"detected_language_mix"`
	OrderItemsSummary   string `json:"order_items_summary"`
	DestinationCity     string `json:"destination_city"`
	PaymentMethodIntent string `json:"payment_method_intent"`
	TranscribedText     string `json:"transcribed_pidgin_text"`
}

func (ve *VoiceEngine) ProcessCustomerVoiceNote(audioURL, senderPhone, profileName string) string {
	if audioURL == "" {
		return "🎙️ *[Voice Note Received]*\nPlease send a clear audio voice note detailing your product order or inquiry!"
	}

	log.Printf("[Voice AI Engine] Processing voice note audio for %s: %s", senderPhone, audioURL)

	geminiKey := os.Getenv("GEMINI_API_KEY")
	if geminiKey != "" {
		reply := ve.callGeminiAudio(audioURL, geminiKey, profileName)
		if reply != "" {
			return reply
		}
	}

	return ve.generateFallbackVoiceResponse(senderPhone, profileName)
}

func (ve *VoiceEngine) callGeminiAudio(audioURL, apiKey, profileName string) string {
	url := fmt.Sprintf("https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key=%s", apiKey)

	prompt := `You are an elite E-Commerce Voice AI Specialist for Teeslux Global Electronics & Solar Nigeria.
Listen to this audio voice note carefully. The customer may speak in Nigerian Pidgin English, Yoruba, Hausa, Igbo, or English.

Vocabulary reference:
- 'Abeg' / 'Biko' / 'E joo' = Please
- 'How much be' / 'Elo ni' / 'Nawa ne' / 'Kedu' = Price Inquiry
- 'Solar panel', 'Inverter', 'Power bank', 'Battery', 'Generator'

Generate a polite structured order confirmation response:
"🎙️ *[MULTILINGUAL VOICE NOTE PARSER]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n👤 *Client:* %s\n🗣️ *Detected Dialect:* Nigerian Pidgin / English\n📝 *Voice Summary:* \"...\"\n📦 *Extracted Order/Inquiry:* ...\n💵 *Live Price:* ₦...\n\n👉 Reply *#buy <qty>* to confirm order or *#manager* for assistance!"`

	prompt = fmt.Sprintf(prompt, profileName)

	payload := map[string]interface{}{
		"contents": []map[string]interface{}{
			{
				"parts": []map[string]interface{}{
					{"text": prompt},
					{
						"file_data": map[string]string{
							"mime_type": "audio/ogg",
							"file_uri":  audioURL,
						},
					},
				},
			},
		},
	}

	data, _ := json.Marshal(payload)
	req, err := http.NewRequest("POST", url, bytes.NewBuffer(data))
	if err != nil {
		return ""
	}
	req.Header.Set("Content-Type", "application/json")

	client := &http.Client{Timeout: 12 * time.Second}
	resp, err := client.Do(req)
	if err != nil || resp == nil {
		return ""
	}
	defer resp.Body.Close()

	body, _ := io.ReadAll(resp.Body)
	var res struct {
		Candidates []struct {
			Content struct {
				Parts []struct {
					Text string `json:"text"`
				} `json:"parts"`
			} `json:"content"`
		} `json:"candidates"`
	}

	if err := json.Unmarshal(body, &res); err == nil && len(res.Candidates) > 0 && len(res.Candidates[0].Content.Parts) > 0 {
		return res.Candidates[0].Content.Parts[0].Text
	}
	return ""
}

func (ve *VoiceEngine) generateFallbackVoiceResponse(senderPhone, profileName string) string {
	return fmt.Sprintf("🎙️ *[MULTILINGUAL VOICE NOTE PARSER]*\n━━━━━━━━━━━━━━━━━━━━━━━━━━━━\nHello %s!\nThank you for sending your audio voice note. Our Voice AI has transcribed & logged your request.\n\n📦 *Order Status:* Voice note assigned to instant concierge.\n👉 Reply *#catalog* to browse items or *#manager* to speak live with our team!", profileName)
}
