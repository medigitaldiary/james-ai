import ReactMarkdown from 'react-markdown'
import type { Message } from '../../types'
import { formatTime } from '../../utils/formatTime'
import { JamesAvatar } from './JamesAvatar'
import { DisclaimerBadge } from './DisclaimerBadge'
import { MessageFeedback } from './MessageFeedback'
import { BondsTable } from './BondsTable'

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
        <div className="bg-white/20 backdrop-blur-md border border-white/30 rounded-2xl rounded-tl-sm px-4 py-3 text-sm text-white leading-relaxed shadow-sm">
          <ReactMarkdown
            components={{
              h1: ({ children }) => <h1 className="text-base font-bold text-white mb-2 mt-3 first:mt-0">{children}</h1>,
              h2: ({ children }) => <h2 className="text-sm font-bold text-white mb-1.5 mt-3 first:mt-0">{children}</h2>,
              h3: ({ children }) => <h3 className="text-sm font-semibold text-white mb-1 mt-2 first:mt-0">{children}</h3>,
              p: ({ children }) => <p className="text-white mb-2 last:mb-0">{children}</p>,
              strong: ({ children }) => <strong className="font-semibold text-white">{children}</strong>,
              em: ({ children }) => <em className="italic text-white/90">{children}</em>,
              ul: ({ children }) => <ul className="mb-2 space-y-0.5 pl-3">{children}</ul>,
              ol: ({ children }) => <ol className="mb-2 space-y-0.5 pl-3 list-decimal">{children}</ol>,
              li: ({ children }) => (
                <li className="text-white flex gap-2">
                  <span className="text-white/60 shrink-0">•</span>
                  <span>{children}</span>
                </li>
              ),
              a: ({ href, children }) => (
                <a href={href} target="_blank" rel="noopener noreferrer" className="text-blue-200 underline hover:text-white transition-colors">
                  {children}
                </a>
              ),
              code: ({ children }) => <code className="bg-white/10 px-1 py-0.5 rounded text-xs font-mono text-white/90">{children}</code>,
              hr: () => <hr className="border-white/20 my-2" />,
            }}
          >
            {message.content}
          </ReactMarkdown>
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
