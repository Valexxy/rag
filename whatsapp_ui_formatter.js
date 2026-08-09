/**
 * ====================================================================
 * RICH WHATSAPP UI FORMATTER (NODE.JS ENGINE v2030)
 * ====================================================================
 * Formats ground-breaking WhatsApp cards for Node.js server.
 */

class WhatsAppUIFormatter {
  static formatProductCard(item, bizName = "Teeslux Global Store") {
    const priceFormatted = Number(item.price || 0).toLocaleString();
    const desc = item.desc || item.description || "High quality product";
    const status = item.status || "In Stock";

    return `🛍️ *[${bizName} — Product Specification]*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `✅ *Product:* \`${item.name}\`\n` +
      `💰 *Price:* \`₦${priceFormatted}.00\` *(Fixed Rate)*\n` +
      `📦 *Availability:* \`${status}\`\n` +
      `📝 *Description:* ${desc}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💬 *Quick Actions:*\n` +
      `• Reply \`1\` or \`#buy\` to place an instant order\n` +
      `• Reply \`#human\` to speak with our Store Manager`;
  }

  static formatDisambiguationCarousel(options, category, bizName = "Teeslux Global Store") {
    const icons = ["1️⃣", "2️⃣", "3️⃣", "4️⃣", "5️⃣"];
    const lines = options.slice(0, 5).map((opt, i) => {
      const icon = icons[i] || `${i + 1}️⃣`;
      const priceFormatted = Number(opt.price || 0).toLocaleString();
      return `${icon} *${opt.name}*\n   └ 💰 Price: \`₦${priceFormatted}.00\``;
    });

    return `🤔 *[${bizName} — ${category.toUpperCase()} Options Available]*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `I found multiple top-quality items matching *'${category}'*:\n\n` +
      lines.join('\n\n') + `\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💬 *Reply with 1, 2, or 3* to inspect full specs & order!`;
  }

  static formatManagerHandover(query, bizName = "Teeslux Global Store", ownerPhone = "2348072015725") {
    return `🚨 *[${bizName} — High-Priority Executive Transfer]*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `Thank you for your inquiry regarding:\n` +
      `❓ *'${query}'*\n\n` +
      `⚡ *Status:* Transferred to Store Manager on **HIGHEST PRIORITY**\n` +
      `⏱️ *Response Time:* Manager will reply directly to your chat shortly!\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `📞 *Direct Escalation:* Call/WhatsApp \`+${ownerPhone}\``;
  }
}

module.exports = WhatsAppUIFormatter;
