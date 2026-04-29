import { ChatArea } from '../chat/ChatArea'
import { Navbar } from './Navbar'
import { usePageContext } from '../../hooks/usePageContext'
export function AppShell() {
  usePageContext()

  return (
    <div
      className="relative flex flex-col h-screen w-screen overflow-hidden"
      style={{ background: '#0E237D url(/bg-new.svg) center/cover no-repeat' }}
    >
      {/* UI layer */}
      <div className="relative z-10 flex flex-col h-full w-full">
        <Navbar />
        <ChatArea />
      </div>
    </div>
  )
}
