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
    <div className="mt-3 -mx-1 overflow-x-auto rounded-xl border border-james-border shadow-sm">
      <table className="min-w-full text-xs border-collapse">
        <thead>
          <tr className="bg-james-primary text-white">
            {[
              'ISIN',
              'Issuer Name',
              'Credit Rating',
              'Face Value',
              'Yield (YTM)',
              'Coupon',
              'Maturity Date',
              'Details',
            ].map((col) => (
              <th
                key={col}
                className="px-3 py-2.5 text-left font-semibold whitespace-nowrap text-[11px] tracking-wide first:rounded-tl-xl last:rounded-tr-xl"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {bonds.map((bond, i) => (
            <tr
              key={bond.isin}
              className={`border-t border-james-border transition-colors hover:bg-james-primary/5 ${
                i % 2 === 0 ? 'bg-white' : 'bg-[#F8F9FD]'
              }`}
            >
              {/* ISIN */}
              <td className="px-3 py-2.5 font-mono text-[11px] text-james-primary font-medium whitespace-nowrap">
                {bond.isin}
              </td>

              {/* Issuer Name */}
              <td className="px-3 py-2.5 text-james-text font-medium max-w-[160px]">
                <span className="line-clamp-2 leading-tight">{bond.registered_name.trim()}</span>
              </td>

              {/* Credit Rating */}
              <td className="px-3 py-2.5 whitespace-nowrap">
                <span className="inline-block text-[11px] font-semibold px-2 py-0.5 rounded-full border border-james-border bg-james-light text-james-primary">
                  {bond.credit_rating}
                </span>
                <span className="block text-[10px] text-james-muted mt-0.5">{bond.rating_agency}</span>
              </td>

              {/* Face Value */}
              <td className="px-3 py-2.5 text-james-text whitespace-nowrap">
                {formatCurrency(bond.face_value)}
              </td>

              {/* Yield */}
              <td className="px-3 py-2.5 whitespace-nowrap">
                <span className="font-bold text-emerald-700">{bond.yield_pct}%</span>
              </td>

              {/* Coupon */}
              <td className="px-3 py-2.5 text-james-text whitespace-nowrap">
                {bond.coupon_rate ? `${bond.coupon_rate}%` : '—'}
                <span className="block text-[10px] text-james-muted">{bond.interest_payout_frequency}</span>
              </td>

              {/* Maturity Date */}
              <td className="px-3 py-2.5 text-james-text whitespace-nowrap">
                {formatDate(bond.maturity_date)}
              </td>

              {/* CTA */}
              <td className="px-3 py-2.5">
                <a
                  href={`https://bondscanner.com/deal-details/${bond.isin}`}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-flex items-center gap-1 bg-james-primary hover:bg-james-primaryHover text-white text-[10px] font-semibold px-2.5 py-1.5 rounded-lg transition-colors whitespace-nowrap"
                >
                  View <ExternalLink size={9} />
                </a>
              </td>
            </tr>
          ))}
        </tbody>
      </table>

      <div className="px-3 py-2 bg-[#F8F9FD] border-t border-james-border rounded-b-xl flex items-center justify-between">
        <p className="text-[10px] text-james-muted">
          Showing {bonds.length} bond{bonds.length !== 1 ? 's' : ''} · Live data from BondScanner
        </p>
        <a
          href="https://bondscanner.com"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] text-james-primary font-medium hover:underline"
        >
          View all on bondscanner.com →
        </a>
      </div>
    </div>
  )
}
