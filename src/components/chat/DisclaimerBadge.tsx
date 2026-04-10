import { Info } from 'lucide-react'
import { SEBI_DISCLAIMER } from '../../config/brand'

export function DisclaimerBadge() {
  return (
    <div className="mt-3 flex gap-1.5 rounded-lg bg-james-disclaimer border border-james-disclaimerBorder px-3 py-2">
      <Info size={12} className="text-amber-500 mt-0.5 shrink-0" />
      <p className="text-xs text-amber-700 leading-relaxed italic">
        {SEBI_DISCLAIMER}
      </p>
    </div>
  )
}
