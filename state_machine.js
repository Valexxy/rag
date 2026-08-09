/**
 * ====================================================================
 * PERSISTED DIALOGUE STATE MACHINE & CHATWOOT MUTING (NODE.JS v2030)
 * ====================================================================
 */

class DialogueStateMachine {
  constructor() {
    this.sessions = new Map();
  }

  getSession(remoteJid) {
    const key = String(remoteJid).trim().toLowerCase();
    if (!this.sessions.has(key)) {
      this.sessions.set(key, { state: 'IDLE', updatedAt: Date.now(), slots: {} });
    }
    return this.sessions.get(key);
  }

  setState(remoteJid, state, slots = {}) {
    const session = this.getSession(remoteJid);
    session.state = state;
    session.updatedAt = Date.now();
    Object.assign(session.slots, slots);
    console.log(`[State Machine] JID '${remoteJid}' -> State: '${state}'`);
  }

  isBotMuted(remoteJid) {
    const session = this.getSession(remoteJid);
    return session.state === 'HUMAN_ESCALATED';
  }

  handleManagerCommand(text) {
    const raw = String(text).trim();

    if (raw.startsWith("#reply")) {
      const parts = raw.substring(6).trim().split("|");
      if (parts.length >= 2) {
        const targetPhone = parts[0].replace(/\D/g, '');
        const message = parts.slice(1).join('|').trim();
        return { isCommand: true, type: 'REPLY', targetPhone, message };
      }
    }

    if (raw.startsWith("#resolve")) {
      const targetPhone = raw.substring(8).replace(/\D/g, '');
      if (targetPhone) {
        this.setState(`${targetPhone}@s.whatsapp.net`, 'IDLE');
        return { isCommand: true, type: 'RESOLVE', targetPhone };
      }
    }

    if (raw.startsWith("#mute")) {
      const targetPhone = raw.substring(5).replace(/\D/g, '');
      if (targetPhone) {
        this.setState(`${targetPhone}@s.whatsapp.net`, 'HUMAN_ESCALATED');
        return { isCommand: true, type: 'MUTE', targetPhone };
      }
    }

    return { isCommand: false };
  }
}

module.exports = new DialogueStateMachine();
