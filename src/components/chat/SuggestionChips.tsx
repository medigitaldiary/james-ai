import { useState, useEffect } from 'react'
import { useChatStore } from '../../store/chatStore'
import { useSendMessage } from '../../hooks/useSendMessage'

const SUGGESTIONS = [
  'What is BondScanner?',
  'I want to open an account',
  'I want to buy bonds',
  'List all AAA-rated bonds',
  'Show bonds above 12% yield',
  'What is YTM?',
  'How do I complete my KYC?',
  'What is a corporate bond?',
  'What is coupon rate?',
  'What documents do I need?',
  'List down live bonds',
  'How does credit rating work?',
]

const VISIBLE_COUNT = 6
const ROTATE_INTERVAL = 5000

export function SuggestionChips() {
  const messages = useChatStore((s) => s.messages)
  const isLoading = useChatStore((s) => s.isLoading)
  const { send } = useSendMessage()
  const [offset, setOffset] = useState(0)
  const [visible, setVisible] = useState(true)

  useEffect(() => {
    const timer = setInterval(() => {
      setVisible(false)
      setTimeout(() => {
        setOffset((prev) => (prev + VISIBLE_COUNT) % SUGGESTIONS.length)
        setVisible(true)
      }, 300)
    }, ROTATE_INTERVAL)
    return () => clearInterval(timer)
  }, [])

  if (messages.length > 0) return null

  const chips = Array.from({ length: VISIBLE_COUNT }, (_, i) =>
    SUGGESTIONS[(offset + i) % SUGGESTIONS.length]
  )

  return (
    <div
      className="grid grid-cols-3 gap-2 mt-[31px] transition-opacity duration-300"
      style={{ opacity: visible ? 1 : 0 }}
    >
      {chips.map((chip) => (
        <button
          key={chip}
          onClick={() => !isLoading && send(chip)}
          disabled={isLoading}
          className="text-xs px-3 py-2 rounded-xl border border-james-border bg-white text-james-muted hover:border-james-primary/40 hover:text-james-primary hover:bg-james-primary/5 transition-all disabled:opacity-40 disabled:cursor-not-allowed text-left leading-snug shadow-sm"
        >
          {chip}
        </button>
      ))}
    </div>
  )
}
