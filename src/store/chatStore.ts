import { create } from 'zustand'
import type { Message } from '../types'
import { FRUSTRATION_TURN_THRESHOLD } from '../config/brand'

interface ChatState {
  messages: Message[]
  isLoading: boolean
  frustrationCount: number
  isFrustrated: boolean
  pageUrl: string

  appendMessage: (msg: Message) => void
  setLoading: (val: boolean) => void
  incrementFrustration: () => void
  flagFrustration: () => void
  dismissFrustration: () => void
  setPageUrl: (url: string) => void
  clearMessages: () => void
}

export const useChatStore = create<ChatState>((set) => ({
  messages: [],
  isLoading: false,
  frustrationCount: 0,
  isFrustrated: false,
  pageUrl: '',

  appendMessage: (msg) =>
    set((state) => ({ messages: [...state.messages, msg] })),

  setLoading: (val) => set({ isLoading: val }),

  incrementFrustration: () =>
    set((state) => {
      const next = state.frustrationCount + 1
      return {
        frustrationCount: next,
        isFrustrated: next >= FRUSTRATION_TURN_THRESHOLD || state.isFrustrated,
      }
    }),

  flagFrustration: () => set({ isFrustrated: true }),

  dismissFrustration: () => set({ isFrustrated: false }),

  setPageUrl: (url) => set({ pageUrl: url }),

  clearMessages: () =>
    set({ messages: [], frustrationCount: 0, isFrustrated: false }),
}))
