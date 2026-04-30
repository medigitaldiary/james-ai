import { Share2 } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { shareConversation } from '../../utils/shareConversation'

export function Navbar() {
  const messages = useChatStore((s) => s.messages)
  const hasConversation = messages.length > 0

  return (
    <nav className="w-full px-4 sm:px-6 py-3 flex items-center justify-between shrink-0">
      {/* Logo */}
      <a href="https://bondscanner.com">
        <img src="/bondscanner-logo.png" alt="BondScanner" className="h-6 sm:h-8" />
      </a>

      {/* Right side actions */}
      <div className="flex items-center gap-2 sm:gap-3">
        {/* Share conversation — only when chat has started */}
        {hasConversation && (
          <button
            onClick={() => shareConversation(messages)}
            className="flex items-center gap-1.5 text-xs sm:text-sm font-medium text-white/70 hover:text-white border border-white/30 hover:border-white/60 px-2.5 sm:px-3 py-1.5 sm:py-2 rounded-lg transition-all"
          >
            <Share2 size={13} />
            <span className="hidden sm:inline">Share</span>
          </button>
        )}

        {/* Sign up CTA */}
        <a
          href="https://bondscanner.com/?login=phone"
          target="_blank"
          rel="noopener noreferrer"
          className="bg-james-primary hover:bg-james-primaryHover text-white text-xs sm:text-sm font-medium px-3 sm:px-4 py-1.5 sm:py-2 rounded-lg transition-colors"
        >
          Sign up
        </a>
      </div>
    </nav>
  )
}
