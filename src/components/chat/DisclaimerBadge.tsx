import { Info } from 'lucide-react'
import { SEBI_DISCLAIMER } from '../../config/brand'

export function DisclaimerBadge() {
  return (
    <div className="mt-3 flex gap-1.5 rounded-lg bg-amber-400/20 backdrop-blur-sm border border-amber-300/40 px-3 py-2">
      <Info size={12} className="text-amber-200 mt-0.5 shrink-0" />
      <p className="text-xs text-amber-100 leading-relaxed italic">
        {SEBI_DISCLAIMER}
      </p>
    </div>
  )
}
