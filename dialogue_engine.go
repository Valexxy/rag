package main

import (
	"fmt"
	"strings"
	"sync"
)

type ChatTurn struct {
	Role    string
	Content string
}

type DialogueEngine struct {
	mu           sync.RWMutex
	states       map[string]string
	memoryThreads map[string][]ChatTurn
}

var globalDialogueEngine = &DialogueEngine{
	states:        make(map[string]string),
	memoryThreads: make(map[string][]ChatTurn),
}

func (d *DialogueEngine) GetState(phone string) string {
	d.mu.RLock()
	defer d.mu.RUnlock()
	state, exists := d.states[phone]
	if !exists {
		return "IDLE"
	}
	return state
}

func (d *DialogueEngine) SetState(phone, state string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	d.states[phone] = state
}

func (d *DialogueEngine) AddTurn(phone, role, content string) {
	d.mu.Lock()
	defer d.mu.Unlock()
	turns := d.memoryThreads[phone]
	turns = append(turns, ChatTurn{Role: role, Content: content})
	if len(turns) > 14 {
		turns = turns[len(turns)-14:]
	}
	d.memoryThreads[phone] = turns
}

func (d *DialogueEngine) HandleManagerCommand(command, senderPhone string) (bool, string) {
	cmd := strings.TrimSpace(command)
	if !strings.HasPrefix(cmd, "#") {
		return false, ""
	}

	parts := strings.SplitN(cmd, " ", 2)
	action := strings.ToLower(parts[0])

	switch action {
	case "#reply":
		if len(parts) < 2 {
			return true, "ERROR: Usage `#reply <customer_phone> | <message>`"
		}
		sub := strings.SplitN(parts[1], "|", 2)
		if len(sub) < 2 {
			return true, "ERROR: Usage `#reply <customer_phone> | <message>`"
		}
		targetPhone := strings.TrimSpace(sub[0])
		msgText := strings.TrimSpace(sub[1])

		replyPayload := fmt.Sprintf("💬 *[Store Manager]:* %s\n\n📞 *Tap to Call Manager (GSM):* tel:+%s\n💬 *Tap to Chat Manager:* https://wa.me/%s", msgText, senderPhone, senderPhone)
		globalWhatsAppEngine.SendMessage("sovereign-ai-master", targetPhone, replyPayload)
		return true, fmt.Sprintf("✅ Message delivered to customer `%s`.", targetPhone)

	case "#resolve", "#unmute":
		if len(parts) >= 2 {
			targetPhone := strings.TrimSpace(parts[1])
			d.SetState(targetPhone, "IDLE")
			return true, fmt.Sprintf("✅ Conversation with `%s` marked RESOLVED. Bot un-muted.", targetPhone)
		}

	case "#mute":
		if len(parts) >= 2 {
			targetPhone := strings.TrimSpace(parts[1])
			d.SetState(targetPhone, "HUMAN_ESCALATED")
			return true, fmt.Sprintf("🤫 Bot MUTED for customer `%s`.", targetPhone)
		}
	}

	return false, ""
}
