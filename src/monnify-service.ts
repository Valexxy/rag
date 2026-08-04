import axios from 'axios';

export interface MonnifyPaymentResponse {
  success: boolean;
  checkoutUrl?: string;
  paymentReference?: string;
  message: string;
}

/**
 * Helper to clean environment variable strings.
 */
function cleanEnvVar(val: string | undefined, defaultValue: string = ''): string {
  if (!val) return defaultValue;
  return val.replace(/^["']|["']$/g, '').trim();
}

/**
 * Generates a Monnify Payment Link / Reserved Transaction.
 * Supports Live API calls as well as a zero-dependency Mock Sandbox mode.
 */
export async function createMonnifyPayment(
  customerName: string,
  customerEmail: string,
  amount: number,
  paymentDescription: string,
  tenantId: string
): Promise<MonnifyPaymentResponse> {
  const isMockMode = process.env.MOCK_MONNIFY === 'true';

  // 1. Build Sanitized Transaction Reference
  const cleanTenant = (tenantId || 'TENANT').replace(/[^a-zA-Z0-9]/g, '').slice(0, 5).toUpperCase();
  const transactionRef = `TX-MOCK-${cleanTenant}-${Date.now()}`;

  // --------------------------------------------------------------------------
  // MOCK SANDBOX MODE (Use for local testing without external API dependency)
  // --------------------------------------------------------------------------
  if (isMockMode) {
    console.log('🧪 [MOCK MONNIFY SANDBOX] Generating simulated transaction...');
    
    // Simulate slight network latency
    await new Promise((resolve) => setTimeout(resolve, 500));

    const mockCheckoutUrl = `https://sandbox.monnify.com/checkout/${transactionRef}`;

    return {
      success: true,
      checkoutUrl: mockCheckoutUrl,
      paymentReference: transactionRef,
      message: `[MOCK] Payment link created: ${mockCheckoutUrl}`
    };
  }

  // --------------------------------------------------------------------------
  // LIVE API ENGINE
  // --------------------------------------------------------------------------
  try {
    const baseUrl = cleanEnvVar(process.env.MONNIFY_BASE_URL, 'https://api.monnify.com');
    const apiKey = cleanEnvVar(process.env.MONNIFY_API_KEY);
    const secretKey = cleanEnvVar(process.env.MONNIFY_SECRET_KEY);
    const contractCode = cleanEnvVar(process.env.MONNIFY_CONTRACT_CODE);
    const redirectUrl = cleanEnvVar(process.env.MONNIFY_REDIRECT_URL, 'https://yourdomain.com/payment-success');

    if (!apiKey || !secretKey || !contractCode) {
      console.warn('⚠️ [MONNIFY CONFIG WARNING]: Missing production keys. Falling back to Mock response.');
      const mockCheckoutUrl = `https://sandbox.monnify.com/checkout/${transactionRef}`;
      return {
        success: true,
        checkoutUrl: mockCheckoutUrl,
        paymentReference: transactionRef,
        message: `[MOCK FALLBACK] Payment link created: ${mockCheckoutUrl}`
      };
    }

    // Authenticate with Monnify
    const authHeader = Buffer.from(`${apiKey}:${secretKey}`).toString('base64');
    const authResponse = await axios.post(
      `${baseUrl}/api/v1/auth/login`,
      {},
      {
        headers: {
          Authorization: `Basic ${authHeader}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const accessToken = authResponse.data?.responseBody?.accessToken;
    if (!accessToken) {
      throw new Error('Failed to extract access token from Monnify response.');
    }

    // Initialize Transaction
    const payload = {
      amount: Number(amount),
      customerName: customerName || 'Valued Customer',
      customerEmail: customerEmail || 'customer@example.com',
      paymentReference: transactionRef,
      paymentDescription: paymentDescription || 'Order Checkout Payment',
      currencyCode: 'NGN',
      contractCode: contractCode,
      redirectUrl: redirectUrl,
      paymentMethods: ['CARD', 'ACCOUNT_TRANSFER']
    };

    const payResponse = await axios.post(
      `${baseUrl}/api/v1/merchant/transactions/init-transaction`,
      payload,
      {
        headers: {
          Authorization: `Bearer ${accessToken}`,
          'Content-Type': 'application/json'
        }
      }
    );

    const checkoutUrl = payResponse.data?.responseBody?.checkoutUrl;

    if (!checkoutUrl) {
      throw new Error('Transaction initialization succeeded, but checkoutUrl was missing.');
    }

    return {
      success: true,
      checkoutUrl: checkoutUrl,
      paymentReference: transactionRef,
      message: `Payment link created successfully: ${checkoutUrl}`
    };
  } catch (error: any) {
    const errorLog = error?.response?.data || error.message;
    console.error('❌ [MONNIFY SERVICE ERROR]:', typeof errorLog === 'object' ? JSON.stringify(errorLog, null, 2) : errorLog);

    return {
      success: false,
      message: 'Unable to generate payment link at this moment.'
    };
  }
}