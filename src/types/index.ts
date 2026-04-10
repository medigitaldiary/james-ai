export type MessageRole = 'user' | 'james'

export interface BondEntry {
  isin: string
  registered_name: string
  face_value: string
  yield_pct: string
  coupon_rate: string
  maturity_date: string
  inventory_status: string
  interest_payout_frequency: string
  credit_rating: string
  rating_agency: string
}

export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  showDisclaimer: boolean
  bondsData?: BondEntry[]
}

export type KBFileStatus = 'uploading' | 'ready' | 'error'

export interface KBFile {
  id: string
  name: string
  size: number
  uploadedAt: Date
  status: KBFileStatus
}

export interface ChatPayload {
  messages: { role: MessageRole; content: string }[]
  kbFileIds: string[]
  pageUrl: string
}

export interface ApiResponse {
  content: string
  show_disclaimer: boolean
  bonds_data?: BondEntry[]
}
