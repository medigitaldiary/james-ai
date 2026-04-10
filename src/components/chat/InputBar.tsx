import { useState, type KeyboardEvent, useRef, useEffect } from 'react'
import { Send } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'
import { useSendMessage } from '../../hooks/useSendMessage'

export function InputBar() {
  const [text, setText] = useState('')
  const isLoading = useChatStore((s) => s.isLoading)
  const messages = useChatStore((s) => s.messages)
  const { send } = useSendMessage()
  const textareaRef = useRef<HTMLTextAreaElement>(null)

  const handleSend = async () => {
    if (!text.trim() || isLoading) return
    const msg = text
    setText('')
    await send(msg)
  }

  const handleKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  useEffect(() => {
    const ta = textareaRef.current
    if (!ta) return
    ta.style.height = 'auto'
    ta.style.height = `${Math.min(ta.scrollHeight, 120)}px`
  }, [text])

  const isWelcome = messages.length === 0

  return (
    <div className={`w-full ${isWelcome ? 'px-4' : 'border-t border-james-border bg-white px-4 py-3'}`}>
      <div className="max-w-2xl mx-auto">
        {/* Input box */}
        <div className="flex items-end gap-2 px-4 py-3 bg-white border border-james-border rounded-2xl shadow-sm focus-within:border-james-primary/40 focus-within:shadow-md transition-all">
          <textarea
            ref={textareaRef}
            value={text}
            onChange={(e) => setText(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Ask James about bonds or BondScanner..."
            rows={1}
            className="flex-1 bg-transparent text-james-text placeholder:text-james-muted text-sm resize-none outline-none leading-relaxed min-h-[24px]"
            style={{ maxHeight: 120 }}
            disabled={isLoading}
          />
          <button
            onClick={handleSend}
            disabled={!text.trim() || isLoading}
            className="shrink-0 w-8 h-8 rounded-xl bg-james-primary hover:bg-james-primaryHover disabled:opacity-30 disabled:cursor-not-allowed flex items-center justify-center transition-all"
          >
            <Send size={14} className="text-white translate-x-0.5" />
          </button>
        </div>

        {/* Footer */}
        <p className="text-center text-xs text-james-muted mt-3">
          By messaging James AI, you agree to our{' '}
          <a href="https://bondscanner.com" className="underline underline-offset-2 hover:text-james-text">
            Terms & Conditions
          </a>{' '}
          and have read our{' '}
          <a href="https://bondscanner.com" className="underline underline-offset-2 hover:text-james-text">
            Privacy Policy
          </a>
          .
        </p>
      </div>
    </div>
  )
}
