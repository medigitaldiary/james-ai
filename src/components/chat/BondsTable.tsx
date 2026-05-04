import type { BondEntry } from '../../types'
import { ExternalLink } from 'lucide-react'

interface Props {
  bonds: BondEntry[]
}

function formatCurrency(val: string): string {
  const num = parseFloat(val)
  if (isNaN(num)) return '—'
  if (num >= 10000000) return `₹${(num / 10000000).toFixed(0)}Cr`
  if (num >= 100000) return `₹${(num / 100000).toFixed(0)}L`
  if (num >= 1000) return `₹${num.toLocaleString('en-IN', { maximumFractionDigits: 0 })}`
  return `₹${num}`
}

function formatDate(val: string): string {
  if (!val) return '—'
  const d = new Date(val)
  return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' })
}

export function BondsTable({ bonds }: Props) {
  if (!bonds || bonds.length === 0) return null

  return (
    <div className="mt-3 -mx-1 overflow-x-auto rounded-xl border border-white/20 shadow-sm backdrop-blur-md bg-white/10">
      <table className="min-w-full text-xs border-collapse">
        <thead>
          <tr className="bg-white/20 border-b border-white/20">
            <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90 rounded-tl-xl">Issuer</th>
            <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90">Rating</th>
            <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90">Yield</th>
            <th className="hidden sm:table-cell px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90">ISIN</th>
            <th className="hidden sm:table-cell px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90">Min. Investment</th>
            <th className="hidden md:table-cell px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90">Maturity</th>
            <th className="px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide text-white/90 rounded-tr-xl">Details</th>
          </tr>
        </thead>
        <tbody>
          {bonds.map((bond, i) => (
            <tr
              key={bond.isin}
              className={`border-t border-white/10 transition-colors hover:bg-white/10 ${
                i % 2 === 0 ? 'bg-transparent' : 'bg-white/5'
              }`}
            >
              {/* Issuer Name — always visible */}
              <td className="px-3 py-2.5 text-white font-medium max-w-[120px] sm:max-w-[160px]">
                <span className="line-clamp-2 leading-tight text-[11px]">{bond.registered_name.trim()}</span>
              </td>

              {/* Credit Rating — always visible */}
              <td className="px-3 py-2.5 whitespace-nowrap">
                <span className="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full border border-white/30 bg-white/15 text-white">
                  {bond.credit_rating}
                </span>
                <span className="hidden sm:block text-[10px] text-white/50 mt-0.5">{bond.rating_agency}</span>
              </td>

              {/* Yield — always visible */}
              <td className="px-3 py-2.5 whitespace-nowrap">
                <span className="font-bold text-emerald-300 text-[11px]">{bond.yield_pct}%</span>
              </td>

              {/* ISIN — hidden on mobile */}
              <td className="hidden sm:table-cell px-3 py-2.5 font-mono text-[11px] text-blue-200 font-medium whitespace-nowrap">
                {bond.isin}
              </td>

              {/* Min. Investment — hidden on mobile */}
              <td className="hidden sm:table-cell px-3 py-2.5 text-white/80 whitespace-nowrap text-[11px]">
                {formatCurrency(bond.face_value)}
              </td>

              {/* Maturity — hidden on mobile + tablet */}
              <td className="hidden md:table-cell px-3 py-2.5 text-white/80 whitespace-nowrap text-[11px]">
                {formatDate(bond.maturity_date)}
              </td>

              {/* CTA — always visible */}
              <td className="px-3 py-2.5">
                <a
                  href={`https://bondscanner.com/deal-details/${bond.isin}${bond.deal_id ? `?id=${bond.deal_id}` : ''}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 bg-white/20 hover:bg-white/30 border border-white/30 text-white text-[10px] font-semibold px-2.5 py-1.5 rounded-lg transition-colors whitespace-nowrap backdrop-blur-sm"
                >
                  View <ExternalLink size={9} />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="px-3 py-2 border-t border-white/10 rounded-b-xl flex items-center justify-between">
        <p className="text-[10px] text-white/50">
          Showing {bonds.length} bond{bonds.length !== 1 ? 's' : ''} · Live data from BondScanner
        </p>
        <a
          href="https://bondscanner.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] text-white/70 font-medium hover:text-white transition-colors"
        >
          View all on bondscanner.com →
        </a>
      </div>
    </div>
  )
}
