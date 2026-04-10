import { v4 as uuidv4 } from 'uuid'
import type { KBFile } from '../types'
import { apiClient } from './api'

const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

const mockFiles: KBFile[] = []

export async function uploadPDF(file: File): Promise<KBFile> {
  if (USE_MOCK) {
    await new Promise((r) => setTimeout(r, 1200))
    const newFile: KBFile = {
      id: uuidv4(),
      name: file.name,
      size: file.size,
      uploadedAt: new Date(),
      status: 'ready',
    }
    mockFiles.push(newFile)
    return newFile
  }

  const formData = new FormData()
  formData.append('file', file)
  const res = await fetch(
    `${import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8000'}/kb/upload`,
    { method: 'POST', body: formData }
  )
  if (!res.ok) throw new Error('Upload failed')
  return res.json()
}

export async function listFiles(): Promise<KBFile[]> {
  if (USE_MOCK) return [...mockFiles]
  return apiClient.post<KBFile[]>('/kb/files', {})
}

export async function deleteFile(id: string): Promise<void> {
  if (USE_MOCK) {
    const idx = mockFiles.findIndex((f) => f.id === id)
    if (idx !== -1) mockFiles.splice(idx, 1)
    return
  }
  await apiClient.delete(`/kb/files/${id}`)
}
