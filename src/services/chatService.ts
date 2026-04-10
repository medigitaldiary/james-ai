import type { ChatPayload, ApiResponse } from '../types'
import { apiClient } from './api'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const MOCK_RESPONSES = [
  "Sure! A **corporate bond** is a debt instrument issued by a company to raise capital. When you invest in a corporate bond, you're essentially lending money to the company. In return, the company pays you interest (the coupon rate) periodically and returns the principal at maturity.",
  "The **YTM (Yield to Maturity)** is the total expected return if you hold a bond until it matures, accounting for the current price, coupon payments, and time remaining. It's one of the most important metrics when comparing bonds on BondScanner.",
  "To complete your **KYC on BondScanner**, you'll need: (1) PAN card, (2) Aadhaar number for e-KYC, and (3) a bank account for linking. Head to the 'Open Account' section and follow the step-by-step flow. Most users complete it in under 10 minutes.",
  "**G-Secs (Government Securities)** are bonds issued by the Indian government — considered the safest fixed-income option since they're backed by the Government of India. **SDLs (State Development Loans)** are similar but issued by state governments. Both are available on BondScanner with competitive yields.",
  "I can see this query might need a more hands-on look. If the issue persists, I can connect you with our support team. You can also reach BondScanner support at support@bondscanner.com.",
]

let mockIndex = 0

async function mockDelay() {
  return new Promise<void>((resolve) =>
    setTimeout(resolve, 1000 + Math.random() * 800)
  )
}

export async function sendMessage(payload: ChatPayload): Promise<ApiResponse> {
  if (USE_MOCK) {
    await mockDelay()
    const content = MOCK_RESPONSES[mockIndex % MOCK_RESPONSES.length]
    mockIndex++
    return { content, show_disclaimer: true }
  }
  return apiClient.post<ApiResponse>('/chat', payload)
}
