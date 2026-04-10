import { FileText, X, Loader2, AlertCircle } from 'lucide-react'
import type { KBFile } from '../../types'

interface Props {
  file: KBFile
  onRemove: (id: string) => void
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`
}

const statusDot: Record<KBFile['status'], string> = {
  ready: 'bg-emerald-400',
  uploading: 'bg-amber-400',
  error: 'bg-red-400',
}

export function FileChip({ file, onRemove }: Props) {
  return (
    <div className="flex items-center gap-2 rounded-lg bg-james-bg border border-james-border px-3 py-2 group">
      {file.status === 'uploading' ? (
        <Loader2 size={14} className="text-james-teal animate-spin shrink-0" />
      ) : file.status === 'error' ? (
        <AlertCircle size={14} className="text-red-400 shrink-0" />
      ) : (
        <FileText size={14} className="text-james-teal shrink-0" />
      )}

      <div className="flex-1 min-w-0">
        <p className="text-xs text-james-text truncate font-medium">{file.name}</p>
        <p className="text-xs text-james-muted">{formatSize(file.size)}</p>
      </div>

      <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${statusDot[file.status]}`} />

      {file.status !== 'uploading' && (
        <button
          onClick={() => onRemove(file.id)}
          className="text-james-muted hover:text-red-400 transition-colors shrink-0 opacity-0 group-hover:opacity-100"
        >
          <X size={12} />
        </button>
      )}
    </div>
  )
}
