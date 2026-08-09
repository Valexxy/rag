/**
 * ====================================================================
 * CROSS-TENANT DISCOVERY & STORE SWITCHING ENGINE (NODE.JS v2030)
 * ====================================================================
 */

class StoreSwitchingEngine {
  constructor() {
    this.userStoreContext = new Map();
  }

  getUserStore(remoteJid) {
    const key = String(remoteJid).toLowerCase().trim();
    const ctx = this.userStoreContext.get(key);
    if (!ctx) return null;

    // 4-hour session timeout auto-reset
    if (Date.now() - ctx.lastActive > 14400000) {
      this.userStoreContext.delete(key);
      return null;
    }

    ctx.lastActive = Date.now();
    return ctx;
  }

  setUserStore(remoteJid, instanceName, tenantData) {
    const key = String(remoteJid).toLowerCase().trim();
    this.userStoreContext.set(key, {
      instanceName,
      tenantData,
      lastActive: Date.now()
    });
  }

  formatStoreChooserMenu(tenants) {
    const icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"];
    const lines = tenants.slice(0, 5).map((t, i) => {
      const icon = icons[i] || `${i + 1}️⃣`;
      const biz = t.business_name || "Store";
      const niche = (t.niche || "retail").toUpperCase();
      return `${icon} *${biz}* \`(${niche})\``;
    });

    return `🏢 *[Sovereign Global Multi-Store Hub]*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `Welcome! Which store would you like to shop with today?\n\n` +
      lines.join('\n') + `\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💬 Reply 1, 2, 3, or 4 to enter store!\n` +
      `💡 Reply \`#switch\` anytime to change stores.`;
  }
}

module.exports = new StoreSwitchingEngine();
