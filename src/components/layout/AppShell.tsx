import { ChatArea } from '../chat/ChatArea'
import { Navbar } from './Navbar'
import { usePageContext } from '../../hooks/usePageContext'

export function AppShell() {
  usePageContext()

  return (
    <div className="flex flex-col h-screen w-screen overflow-hidden bg-james-bg">
      <Navbar />
      <ChatArea />
    </div>
  )
}
