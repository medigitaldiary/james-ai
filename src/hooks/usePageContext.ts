import { useEffect } from 'react'
import { useChatStore } from '../store/chatStore'

export function usePageContext() {
  const setPageUrl = useChatStore((s) => s.setPageUrl)
  const pageUrl = useChatStore((s) => s.pageUrl)

  useEffect(() => {
    setPageUrl(window.location.href)
  }, [setPageUrl])

  return pageUrl
}
