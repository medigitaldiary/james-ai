import type { Message } from '../../types'
import { formatTime } from '../../utils/formatTime'
import { JamesAvatar } from './JamesAvatar'
import { DisclaimerBadge } from './DisclaimerBadge'
import { MessageFeedback } from './MessageFeedback'
import { BondsTable } from './BondsTable'

function renderContent(text: string) {
  const parts = text.split(/(\*\*[^*]+\*\*)/g)
  return parts.map((part, i) => {
    if (part.startsWith('**') && part.endsWith('**')) {
      return <strong key={i} className="font-semibold text-white">{part.slice(2, -2)}</strong>
    }
    return <span key={i}>{part}</span>
  })
}

interface Props {
  message: Message
  userQuery: string
}

export function JamesBubble({ message, userQuery }: Props) {
  return (
    <div className="flex items-start gap-3">
      <JamesAvatar size={28} />
      <div className="flex-1 min-w-0 space-y-1">
        <p className="text-xs font-medium text-white/80 mb-1">James</p>
        <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-white leading-relaxed whitespace-pre-wrap shadow-sm">
          {renderContent(message.content)}
          {message.bondsData && message.bondsData.length > 0 && (
            <BondsTable bonds={message.bondsData} />
          )}
          {message.showDisclaimer && <DisclaimerBadge />}
        </div>
        <div className="flex items-center justify-between">
          <p className="text-xs text-white/50 pl-1">
            {formatTime(message.timestamp)}
          </p>
          <MessageFeedback
            messageId={message.id}
            messageContent={message.content}
            userQuery={userQuery}
          />
        </div>
      </div>
    </div>
  )
}
