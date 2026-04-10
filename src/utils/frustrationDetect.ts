import { FRUSTRATION_KEYWORDS } from '../config/brand'

export function detectFrustration(text: string): boolean {
  const lower = text.toLowerCase()
  return FRUSTRATION_KEYWORDS.some((kw) => lower.includes(kw))
}
