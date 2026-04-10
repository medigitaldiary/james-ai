import type { KBFile } from '../../types'
import { FileChip } from '../ui/FileChip'

interface Props {
  files: KBFile[]
  onRemove: (id: string) => void
}

export function FileList({ files, onRemove }: Props) {
  if (files.length === 0) {
    return (
      <p className="text-xs text-james-muted/60 italic text-center py-3">
        No PDFs uploaded yet
      </p>
    )
  }

  return (
    <div className="space-y-2">
      {files.map((file) => (
        <FileChip key={file.id} file={file} onRemove={onRemove} />
      ))}
    </div>
  )
}
