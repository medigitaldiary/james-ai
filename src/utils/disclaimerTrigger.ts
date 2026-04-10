import { DISCLAIMER_TRIGGER_KEYWORDS } from '../config/brand'

export function shouldShowDisclaimer(text: string): boolean {
  const lower = text.toLowerCase()
  return DISCLAIMER_TRIGGER_KEYWORDS.some((kw) => lower.includes(kw))
}
