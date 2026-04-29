import { Share2 } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { shareConversation } from '../../utils/shareConversation'

export function Navbar() {
  const messages = useChatStore((s) => s.messages)
  const hasConversation = messages.length > 0

  return (
    <nav className="w-full px-6 py-3 flex items-center justify-between shrink-0">
      {/* Logo */}
      <a href="https://bondscanner.com">
        <img src="/bondscanner-logo.png" alt="BondScanner" className="h-8" />
      </a>

      {/* Right side actions */}
      <div className="flex items-center gap-3">
        {/* Share conversation — only when chat has started */}
        {hasConversation && (
          <button
            onClick={() => shareConversation(messages)}
            className="flex items-center gap-1.5 text-sm font-medium text-james-muted hover:text-james-primary border border-james-border hover:border-james-primary/40 px-3 py-2 rounded-lg transition-all"
          >
            <Share2 size={14} />
            Share
          </button>
        )}

        {/* Sign up CTA */}
        <a
          href="https://bondscanner.com/?login=phone"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-james-primary hover:bg-james-primaryHover text-white text-sm font-medium px-4 py-2 rounded-lg transition-colors"
        >
          Sign up
        </a>
      </div>
    </nav>
  )
}
