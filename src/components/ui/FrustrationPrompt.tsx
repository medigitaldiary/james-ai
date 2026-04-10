import { AlertCircle, X } from 'lucide-react'
import { useChatStore } from '../../store/chatStore'

export function FrustrationPrompt() {
  const { isFrustrated, dismissFrustration } = useChatStore()

  if (!isFrustrated) return null

  return (
    <div className="flex items-center gap-3 bg-amber-50 border-b border-amber-200 px-6 py-3">
      <AlertCircle size={15} className="text-amber-500 shrink-0" />
      <p className="text-sm text-amber-800 flex-1">
        Having trouble finding what you need?{' '}
        <a
          href="https://api.whatsapp.com/send/?phone=919380740546&text=Hi%2C+I+need+assistance+with+my+account.+Kindly+connect+me+with+a+support+representative&type=phone_number&app_absent=0"
          target="_blank"
          rel="noopener noreferrer"
          className="underline underline-offset-2 font-medium hover:text-amber-900"
        >
          Contact BondScanner support
        </a>
      </p>
      <button
        onClick={dismissFrustration}
        className="text-amber-400 hover:text-amber-600 transition-colors shrink-0"
      >
        <X size={14} />
      </button>
    </div>
  )
}
