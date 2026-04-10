import { JamesAvatar } from './JamesAvatar'

export function TypingIndicator() {
  return (
    <div className="flex items-start gap-3">
      <JamesAvatar size={28} />
      <div className="bg-white border border-james-border rounded-2xl rounded-tl-sm px-4 py-3 shadow-sm">
        <div className="flex gap-1 items-center h-4">
          {[0, 1, 2].map((i) => (
            <span
              key={i}
              className="w-1.5 h-1.5 rounded-full bg-james-muted animate-bounce"
              style={{ animationDelay: `${i * 150}ms`, animationDuration: '0.8s' }}
            />
          ))}
        </div>
      </div>
    </div>
  )
}
