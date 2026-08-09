/**
 * ====================================================================
 * UNIVERSAL MULTI-NICHE GLOBAL BUSINESS ENGINE (NODE.JS v2030)
 * ====================================================================
 */

class NicheFormatter {
  static formatGreeting(bizName, niche, todGreeting, formattedTime, isReturning = false, lastItem = "") {
    niche = (niche || "retail").toLowerCase();

    const configs = {
      real_estate: {
        title: "GRA Prime Properties & Estates",
        tagline: "Premium Real Estate & Property Advisory",
        opt1: "1️⃣ *View Property Listings* — Duplexes, Flats & Land",
        opt2: "2️⃣ *Book Physical Inspection* — Schedule estate tour",
        opt3: "3️⃣ *Lease & Title Documents* — Deed of assignment",
        opt4: "4️⃣ *Talk with Lead Consultant* — Direct consultation"
      },
      healthcare: {
        title: "Apex Specialist Clinic & Care",
        tagline: "24/7 Specialist Medical Services",
        opt1: "1️⃣ *Book Appointment* — Doctor consultation slot",
        opt2: "2️⃣ *Prescription Refill* — Order medications",
        opt3: "3️⃣ *Lab Test Results* — Download diagnostic report",
        opt4: "4️⃣ *Emergency Care* — Direct doctor line"
      },
      hospitality: {
        title: "Grand Imperial Hotel & Resort",
        tagline: "Luxury Accommodations & Dining",
        opt1: "1️⃣ *Room Reservations* — Executive suites & rates",
        opt2: "2️⃣ *Room Service Menu* — Order food to suite",
        opt3: "3️⃣ *Event Hall Booking* — Conferences & weddings",
        opt4: "4️⃣ *Concierge Desk* — Speak with front desk"
      },
      salon: {
        title: "Queens Beauty Salon & Spa",
        tagline: "Royal Hair, Nails & Pampering",
        opt1: "1️⃣ *Hair Styling & Installation* — Wig fixing & braids",
        opt2: "2️⃣ *Spa & Pedicure* — Royal treatment packages",
        opt3: "3️⃣ *Book Appointment Slot* — Select date & time",
        opt4: "4️⃣ *Salon Manager* — Direct booking line"
      },
      automobile: {
        title: "Apex Auto Motors & Service",
        tagline: "Sales, Maintenance & Spare Parts",
        opt1: "1️⃣ *Vehicle Inventory* — Sedans, SUVs & Trucks",
        opt2: "2️⃣ *Book Maintenance Service* — Oil change & repair",
        opt3: "3️⃣ *Order Spare Parts* — Original OEM parts",
        opt4: "4️⃣ *Speak with Master Mechanic* — Technical support"
      },
      retail: {
        title: bizName,
        tagline: "Premium Electronics, Solar & Retail",
        opt1: "1️⃣ *Product Catalog* — View prices & inventory",
        opt2: "2️⃣ *Book Physical Inspection* — Schedule store visit",
        opt3: "3️⃣ *Track Order Shipment* — Delivery status",
        opt4: "4️⃣ *Store Manager* — Executive client care"
      }
    };

    const cfg = configs[niche] || configs.retail;
    const title = niche !== "retail" ? cfg.title : bizName;
    const returningBadge = isReturning ? "\n🌟 *Welcome Back! Resuming your session...*" : "";
    const lastContext = lastItem ? `\n💡 *Last viewed:* '${lastItem}'` : "";

    return `🏛️ *[${title} — Client Experience]*\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n` +
      `${todGreeting}! ${cfg.tagline}.${returningBadge}\n` +
      `🕒 *Current Local Time:* \`${formattedTime}\`\n\n` +
      `How may we serve your request today?${lastContext}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `${cfg.opt1}\n` +
      `${cfg.opt2}\n` +
      `${cfg.opt3}\n` +
      `${cfg.opt4}\n\n` +
      `━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n` +
      `💬 Reply 1, 2, 3, or 4 to proceed!`;
  }
}

module.exports = NicheFormatter;
