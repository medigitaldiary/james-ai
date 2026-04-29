import type { Message } from '../../types'
import { formatTime } from '../../utils/formatTime'

export function UserBubble({ message }: { message: Message }) {
  return (
    <div className="flex justify-end">
      <div className="max-w-[65%] space-y-1">
        <div className="bg-white/30 backdrop-blur-md border border-white/40 text-white rounded-2xl rounded-br-sm px-4 py-3 text-sm leading-relaxed">
          {message.content}
        </div>
        <p className="text-right text-xs text-white/50 pr-1">
          {formatTime(message.timestamp)}
        </p>
      </div>
    </div>
  )
}
