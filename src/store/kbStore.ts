import { create } from 'zustand'
import type { KBFile } from '../types'

interface KBState {
  files: KBFile[]
  addFile: (file: KBFile) => void
  updateFileStatus: (id: string, status: KBFile['status']) => void
  removeFile: (id: string) => void
}

export const useKBStore = create<KBState>((set) => ({
  files: [],

  addFile: (file) =>
    set((state) => ({ files: [...state.files, file] })),

  updateFileStatus: (id, status) =>
    set((state) => ({
      files: state.files.map((f) => (f.id === id ? { ...f, status } : f)),
    })),

  removeFile: (id) =>
    set((state) => ({ files: state.files.filter((f) => f.id !== id) })),
}))
