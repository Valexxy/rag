import { createClient } from '@supabase/supabase-js';
import { pipeline } from '@xenova/transformers';
import dotenv from 'dotenv';
import path from 'path';

dotenv.config({ path: path.resolve(__dirname, '.env') });

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_SERVICE_ROLE_KEY;

if (!supabaseUrl || !supabaseKey) {
  console.error('❌ Missing SUPABASE_URL or SUPABASE_SERVICE_ROLE_KEY in .env!');
  process.exit(1);
}

const supabase = createClient(supabaseUrl, supabaseKey, {
  auth: { persistSession: false, autoRefreshToken: false },
});

export interface ItemInput {
  sku: string;
  name: string;
  brand: string;
  category: string;
  price: number;
  stock_quantity: number; // For services, this represents available daily slots/capacity
  description: string;
  specs: Record<string, any>;
}

function createEmbeddingContext(item: ItemInput): string {
  const stockStatus = item.stock_quantity > 0 
    ? `Available (${item.stock_quantity} units/slots remaining)` 
    : 'Currently Unavailable / Fully Booked';

  const specsFormatted = Object.entries(item.specs || {})
    .map(([key, val]) => `${key}: ${val}`)
    .join(', ');

  return `
Item Name: ${item.name}
Provider/Brand: ${item.brand}
Category: ${item.category}
Price/Fee: $${item.price.toFixed(2)}
Availability: ${stockStatus}
Details: ${specsFormatted}
Description: ${item.description}
  `.trim();
}

export async function upsertProductVector(item: ItemInput, extractor: any) {
  const embeddingContent = createEmbeddingContext(item);

  console.log(`⏳ [${item.sku}] Embedding: ${item.name}...`);

  const output = await extractor(embeddingContent, { pooling: 'mean', normalize: true });
  const embedding = Array.from(output.data);

  const { error } = await supabase
    .from('products')
    .upsert(
      {
        sku: item.sku,
        name: item.name,
        brand: item.brand,
        category: item.category,
        price: item.price,
        stock_quantity: item.stock_quantity,
        description: item.description,
        metadata: item.specs,
        embedding_content: embeddingContent,
        embedding: embedding,
        updated_at: new Date().toISOString(),
      },
      { onConflict: 'sku' }
    );

  if (error) {
    console.error(`❌ Error inserting ${item.sku}:`, error.message);
    throw error;
  }

  console.log(`✅ Indexed: ${item.name}`);
}

// --------------------------------------------------------------------------
// GLOBAL MULTI-NICHE CATALOG (100+ PRODUCTS & PROFESSIONAL SERVICES)
// --------------------------------------------------------------------------
const catalog: ItemInput[] = [
  // --- 1. PHARMACEUTICALS & HEALTHCARE SERVICES ---
  {
    sku: 'MED-PAR-500',
    name: 'Paracetamol 500mg Extra Relief',
    brand: 'PharmAtlas',
    category: 'Pharmaceuticals',
    price: 12.50,
    stock_quantity: 120,
    description: 'Fast-acting pain and fever reducer. Ideal for headaches, toothaches, and body temperature reduction.',
    specs: { dosage: '500mg', form: 'Tablet', pack_size: '24 count' }
  },
  {
    sku: 'MED-IBU-400',
    name: 'Ibuprofen 400mg Anti-Inflammatory',
    brand: 'PharmAtlas',
    category: 'Pharmaceuticals',
    price: 14.20,
    stock_quantity: 85,
    description: 'Targeted relief for swelling, joint inflammation, arthritis, and muscular pain.',
    specs: { dosage: '400mg', form: 'Softgel' }
  },
  {
    sku: 'MED-AMO-250',
    name: 'Amoxicillin Antibiotic 250mg',
    brand: 'HealthCare Co',
    category: 'Pharmaceuticals',
    price: 25.00,
    stock_quantity: 40,
    description: 'Broad-spectrum antibiotic capsule for bacterial infections of the respiratory tract, ear, and skin.',
    specs: { dosage: '250mg', prescription_required: true }
  },
  {
    sku: 'SRV-DOC-TELE',
    name: 'General Telehealth GP Consultation Slot',
    brand: 'Global TeleDoc',
    category: 'Healthcare Services',
    price: 49.99,
    stock_quantity: 12,
    description: '30-minute online video medical consultation with a certified doctor for prescription renewals, general diagnosis, and medical advice.',
    specs: { duration: '30 mins', mode: 'Video Call', emergency_support: false }
  },

  // --- 2. CONSUMER TECH & ENTERPRISE IT SERVICES ---
  {
    sku: 'IPHONE-15-PRO-256',
    name: 'Apple iPhone 15 Pro Titanium',
    brand: 'Apple',
    category: 'Consumer Electronics',
    price: 1099.00,
    stock_quantity: 8,
    description: 'A17 Pro chip, aerospace titanium frame, customizable Action button, 48MP camera, USB-C connectivity.',
    specs: { storage: '256GB', color: 'Natural Titanium' }
  },
  {
    sku: 'MAC-M3-AIR15',
    name: 'Apple MacBook Air 15-inch M3',
    brand: 'Apple',
    category: 'Consumer Electronics',
    price: 1299.00,
    stock_quantity: 10,
    description: 'Ultra-thin laptop powered by the M3 chip. 18-hour battery life, Liquid Retina display.',
    specs: { ram: '16GB', storage: '512GB SSD' }
  },
  {
    sku: 'SRV-IT-WIFI',
    name: 'On-Site Enterprise Wi-Fi & Network Setup Service',
    brand: 'NetPro Solutions',
    category: 'IT Services',
    price: 299.00,
    stock_quantity: 5,
    description: 'Professional technician installation for mesh Wi-Fi routing, firewall configuration, high-speed ethernet cabling, and dead-zone elimination.',
    specs: { coverage: 'Up to 5000 sq ft', response_time: '24 hours' }
  },

  // --- 3. PROFESSIONAL LEGAL, FINANCIAL & CONSULTING SERVICES ---
  {
    sku: 'SRV-LEG-CORP',
    name: 'Business Incorporation & LLC Legal Filing Package',
    brand: 'LexCorp Legal',
    category: 'Legal Services',
    price: 450.00,
    stock_quantity: 20,
    description: 'Complete legal handling of company registration, operating agreements, tax ID (EIN) acquisition, and compliance filing.',
    specs: { turnaround_time: '3 business days', jurisdiction: 'Global/Federal' }
  },
  {
    sku: 'SRV-FIN-TAX',
    name: 'Individual & Small Business Annual Tax Audit & Return Service',
    brand: 'ClearBalance CPAs',
    category: 'Financial Services',
    price: 350.00,
    stock_quantity: 15,
    description: 'Expert CPA tax preparation, deduction optimization, audit protection, and electronic filing.',
    specs: { consultant: 'Licensed CPA', filing_type: 'Federal & State' }
  },

  // --- 4. AUTOMOTIVE PRODUCTS & MECHANICAL SERVICES ---
  {
    sku: 'AUTO-OIL-5W30',
    name: 'Mobil 1 Advanced Full Synthetic Motor Oil 5W-30',
    brand: 'Mobil 1',
    category: 'Automotive Parts',
    price: 38.99,
    stock_quantity: 60,
    description: 'Engine protection for up to 10,000 miles. Reduces engine wear, sludge build-up, and improves fuel economy.',
    specs: { volume: '5 Quarts', viscosity: '5W-30' }
  },
  {
    sku: 'SRV-AUTO-TUNE',
    name: 'Comprehensive Vehicle Brake & Engine Maintenance Service',
    brand: 'SpeedyAuto Workshop',
    category: 'Automotive Services',
    price: 180.00,
    stock_quantity: 8,
    description: 'Full brake pad replacement, rotor inspection, oil filter change, fluid top-up, and multi-point safety check.',
    specs: { duration: '2 hours', warranty: '6 Months / 6,000 Miles' }
  },

  // --- 5. REAL ESTATE & HOSPITALITY SERVICES ---
  {
    sku: 'SRV-RE-APPRAISAL',
    name: 'Certified Residential Property Valuation & Appraisal',
    brand: 'Apex Real Estate Experts',
    category: 'Real Estate Services',
    price: 500.00,
    stock_quantity: 6,
    description: 'Official licensed property appraisal report for mortgage approval, home sales, or insurance coverage.',
    specs: { delivery: 'Digital PDF Report', turnaround: '48 Hours' }
  },
  {
    sku: 'SRV-HOTEL-LUX',
    name: 'Executive Ocean-View Suite Overnight Booking',
    brand: 'Grand Horizon Resort',
    category: 'Hospitality & Travel',
    price: 320.00,
    stock_quantity: 3,
    description: 'Luxury hotel room night stay including complimentary gourmet breakfast, spa access, king-size bed, and ocean balcony.',
    specs: { max_occupancy: '2 Adults', check_in: '3:00 PM' }
  },

  // --- 6. HOME REPAIR, CLEANING & TRADES ---
  {
    sku: 'SRV-PLUMB-EMERGENCY',
    name: '24/7 Emergency Plumbing Leak Repair & Unclogging Service',
    brand: 'PipeMasters 247',
    category: 'Home Services',
    price: 150.00,
    stock_quantity: 10,
    description: 'Immediate dispatch technician for burst pipes, severe drain blockages, water heater failures, and sewer line backup.',
    specs: { dispatch_time: 'Under 45 mins', availability: '24/7' }
  },
  {
    sku: 'SRV-CLEAN-DEEP',
    name: 'Deep Residential Home Cleaning Service (3 Bedroom)',
    brand: 'SparkleClean Co',
    category: 'Home Services',
    price: 220.00,
    stock_quantity: 14,
    description: 'Thorough sanitization of kitchens, bathrooms, carpet vacuuming, floor mopping, window washing, and dust removal.',
    specs: { crew_size: '2 Cleaners', duration: '3.5 hours' }
  },

  // --- 7. BEAUTY, WELLNESS & FITNESS ---
  {
    sku: 'BEAUTY-HYDRA-CRM',
    name: 'La Roche-Posay Hyalu B5 Hyaluronic Acid Serum',
    brand: 'La Roche-Posay',
    category: 'Beauty & Skincare',
    price: 39.99,
    stock_quantity: 50,
    description: 'Anti-aging daily face serum for deep hydration, skin plumpness, and wrinkle reduction.',
    specs: { volume: '30ml', skin_type: 'Sensitive / All' }
  },
  {
    sku: 'SRV-SPA-MASSAGE',
    name: '90-Minute Deep Tissue Body Massage Therapy',
    brand: 'Zenith Wellness Spa',
    category: 'Wellness Services',
    price: 110.00,
    stock_quantity: 7,
    description: 'Therapeutic muscle pain relief session with essential oils, target point acupressure, and hot towel treatment.',
    specs: { duration: '90 minutes', therapist: 'Certified Massage Therapist' }
  }
];

// DYNAMICALLY GENERATE 90+ ADDITIONAL PRODUCTS/SERVICES TO OVERFLOW PAST 100+ ITEMS
const industries = [
  { cat: 'E-Commerce Logistics', brand: 'ShipExpress', names: ['Express Courier Delivery', 'International Air Cargo Slot', 'Warehousing Pallet Storage'] },
  { cat: 'Event Planning', brand: 'Crown Events', names: ['Wedding Photography Package', 'DJ Sound & Lighting Setup', 'Catering Service per Head'] },
  { cat: 'Education & Tutoring', brand: 'BrainAcademy', names: ['SAT Prep 1-on-1 Coaching', 'Full-Stack Coding Bootcamp Slot', 'Language Immersion Class'] },
  { cat: 'Solar & Renewable Energy', brand: 'EcoPower', names: ['5kW Residential Solar Panel Kit', 'Commercial Battery Storage Unit', 'Solar Roof Audit Service'] },
  { cat: 'Fitness & Sports', brand: 'FitPulse', names: ['Personal Trainer Monthly Pass', 'Commercial Treadmill Pro', 'Hydro Whey Protein Powder 2kg'] }
];

let counter = catalog.length + 1;
for (const ind of industries) {
  for (let i = 1; i <= 18; i++) {
    const pName = ind.names[i % ind.names.length];
    catalog.push({
      sku: `GLOB-${counter}`,
      name: `${pName} Option ${i}`,
      brand: ind.brand,
      category: ind.cat,
      price: parseFloat((25 + (counter * 8.5) % 1200).toFixed(2)),
      stock_quantity: (counter * 3) % 40,
      description: `Premium ${ind.cat.toLowerCase()} offering designed to deliver top tier accuracy, compliance, and international satisfaction for demanding customers.`,
      specs: { package_tier: `Tier ${i}`, international_code: `INT-${counter}` }
    });
    counter++;
  }
}

async function runIngestion() {
  console.log('🚀 Loading local MiniLM embedding extractor...\n');
  const extractor = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');

  console.log(`🚀 Ingesting & Indexing ${catalog.length} Products and Professional Services into Supabase...\n`);
  
  let successCount = 0;
  for (const item of catalog) {
    try {
      await upsertProductVector(item, extractor);
      successCount++;
    } catch (err: any) {
      console.error(`⚠️ Failed to ingest ${item.sku}:`, err.message || err);
    }
  }

  console.log(`\n🎉 CATALOG INGESTION COMPLETE! (${successCount}/${catalog.length} Items successfully stored in vector database)`);
}

runIngestion().catch((err) => {
  console.error('Fatal execution failure:', err);
  process.exit(1);
});