import { useChatStore } from '../../store/chatStore'
import { FrustrationPrompt } from '../ui/FrustrationPrompt'
import { MessageList } from './MessageList'
import { InputBar } from './InputBar'
import { WelcomeBanner } from './WelcomeBanner'
import { SuggestionChips } from './SuggestionChips'

export function ChatArea() {
  const messages = useChatStore((s) => s.messages)
  const isWelcome = messages.length === 0

  return (
    <div className="flex flex-col flex-1 min-h-0 bg-james-bg">
      <FrustrationPrompt />

      {/* Message area */}
      <div className="flex flex-col flex-1 min-h-0 overflow-hidden">
        {isWelcome ? (
          <div className="flex-1 flex flex-col items-center justify-center overflow-y-auto">
            <div className="w-full max-w-2xl px-4">
              <WelcomeBanner />
              <InputBar />
              <SuggestionChips />
            </div>
          </div>
        ) : (
          <>
            <MessageList />
            <div className="bg-white border-t border-james-border">
              <InputBar />
            </div>
          </>
        )}
      </div>
    </div>
  )
}
