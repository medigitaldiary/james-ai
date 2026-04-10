import { BookOpen } from 'lucide-react'
import { useKnowledgeBase } from '../../hooks/useKnowledgeBase'
import { UploadZone } from './UploadZone'
import { FileList } from './FileList'

export function KBPanel() {
  const { files, upload, remove, uploadError } = useKnowledgeBase()
  const readyCount = files.filter((f) => f.status === 'ready').length

  return (
    <div className="flex flex-col gap-4">
      <div className="flex items-center gap-2">
        <BookOpen size={14} className="text-james-teal" />
        <span className="text-xs font-semibold text-james-text uppercase tracking-wider">
          Knowledge Base
        </span>
        {readyCount > 0 && (
          <span className="ml-auto text-xs bg-james-teal/20 text-james-teal rounded-full px-2 py-0.5">
            {readyCount}
          </span>
        )}
      </div>

      <UploadZone onUpload={upload} error={uploadError} />

      <FileList files={files} onRemove={remove} />
    </div>
  )
}
