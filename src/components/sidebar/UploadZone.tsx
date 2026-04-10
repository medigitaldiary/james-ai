import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'
import { UploadCloud } from 'lucide-react'

interface Props {
  onUpload: (file: File) => void
  error: string | null
}

export function UploadZone({ onUpload, error }: Props) {
  const onDrop = useCallback(
    (accepted: File[]) => {
      if (accepted[0]) onUpload(accepted[0])
    },
    [onUpload]
  )

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: { 'application/pdf': ['.pdf'] },
    multiple: false,
    maxSize: 20 * 1024 * 1024,
  })

  return (
    <div className="space-y-2">
      <div
        {...getRootProps()}
        className={`border-2 border-dashed rounded-xl p-4 text-center cursor-pointer transition-all ${
          isDragActive
            ? 'border-james-teal bg-james-teal/10'
            : 'border-james-border hover:border-james-teal/50 hover:bg-james-surface/50'
        }`}
      >
        <input {...getInputProps()} />
        <UploadCloud
          size={20}
          className={`mx-auto mb-2 ${isDragActive ? 'text-james-teal' : 'text-james-muted'}`}
        />
        <p className="text-xs text-james-muted leading-relaxed">
          {isDragActive ? (
            <span className="text-james-teal">Drop PDF here</span>
          ) : (
            <>
              Drag & drop a PDF or{' '}
              <span className="text-james-teal underline underline-offset-2">
                browse
              </span>
            </>
          )}
        </p>
        <p className="text-xs text-james-muted/60 mt-1">Max 20 MB</p>
      </div>

      {error && (
        <p className="text-xs text-red-400">{error}</p>
      )}
    </div>
  )
}
