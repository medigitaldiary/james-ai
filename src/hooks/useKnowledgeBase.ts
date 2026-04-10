import { useState } from 'react'
import { v4 as uuidv4 } from 'uuid'
import { useKBStore } from '../store/kbStore'
import { uploadPDF, deleteFile } from '../services/kbService'

export function useKnowledgeBase() {
  const { addFile, updateFileStatus, removeFile, files } = useKBStore()
  const [uploadError, setUploadError] = useState<string | null>(null)

  const upload = async (file: File) => {
    if (file.type !== 'application/pdf') {
      setUploadError('Only PDF files are supported.')
      return
    }
    setUploadError(null)

    const tempId = uuidv4()
    addFile({
      id: tempId,
      name: file.name,
      size: file.size,
      uploadedAt: new Date(),
      status: 'uploading',
    })

    try {
      const uploaded = await uploadPDF(file)
      removeFile(tempId)
      addFile(uploaded)
    } catch {
      updateFileStatus(tempId, 'error')
      setUploadError('Upload failed. Please try again.')
    }
  }

  const remove = async (id: string) => {
    removeFile(id)
    try {
      await deleteFile(id)
    } catch {
      // silent fail for PoC
    }
  }

  return { files, upload, remove, uploadError }
}
