import { useState } from 'react'
import { ThumbsUp, ThumbsDown, Copy, Check } from 'lucide-react'

interface Props {
  messageId: string
  messageContent: string
  userQuery: string
}

type Rating = 'up' | 'down' | null

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'

export function MessageFeedback({ messageId, messageContent, userQuery }: Props) {
  const [rating, setRating] = useState<Rating>(null)
  const [copied, setCopied] = useState(false)
  const [submitting, setSubmitting] = useState(false)

  const handleRating = async (value: 'up' | 'down') => {
    // Toggle off if same rating clicked again
    const newRating = rating === value ? null : value
    setRating(newRating)

    if (!newRating) return

    setSubmitting(true)
    try {
      await fetch(`${API_BASE}/feedback`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          message_id: messageId,
          rating: newRating,
          user_query: userQuery,
          message_content: messageContent,
        }),
      })
    } catch {
      // Silently fail — don't disrupt UX for a feedback error
    } finally {
      setSubmitting(false)
    }
  }

  const handleCopy = async () => {
    try {
      await navigator.clipboard.writeText(messageContent)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    } catch {
      // fallback for older browsers
      const el = document.createElement('textarea')
      el.value = messageContent
      document.body.appendChild(el)
      el.select()
      document.execCommand('copy')
      document.body.removeChild(el)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  return (
    <div className="flex items-center gap-1 pl-1 mt-1">
      {/* Thumbs up */}
      <button
        onClick={() => !submitting && handleRating('up')}
        disabled={submitting}
        title="Helpful"
        className={`p-1.5 rounded-lg transition-all ${
          rating === 'up'
            ? 'text-green-600 bg-green-50'
            : 'text-james-muted hover:text-green-600 hover:bg-green-50'
        }`}
      >
        <ThumbsUp size={13} />
      </button>

      {/* Thumbs down */}
      <button
        onClick={() => !submitting && handleRating('down')}
        disabled={submitting}
        title="Not helpful"
        className={`p-1.5 rounded-lg transition-all ${
          rating === 'down'
            ? 'text-red-500 bg-red-50'
            : 'text-james-muted hover:text-red-500 hover:bg-red-50'
        }`}
      >
        <ThumbsDown size={13} />
      </button>

      {/* Divider */}
      <div className="w-px h-3 bg-james-border mx-0.5" />

      {/* Copy / Share */}
      <button
        onClick={handleCopy}
        title={copied ? 'Copied!' : 'Copy response'}
        className={`p-1.5 rounded-lg transition-all flex items-center gap-1 ${
          copied
            ? 'text-james-primary bg-james-primary/10'
            : 'text-james-muted hover:text-james-primary hover:bg-james-primary/10'
        }`}
      >
        {copied ? <Check size={13} /> : <Copy size={13} />}
        {copied && <span className="text-xs font-medium">Copied</span>}
      </button>
    </div>
  )
}
