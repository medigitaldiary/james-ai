import { ChatArea } from '../chat/ChatArea'
import { Navbar } from './Navbar'
import { usePageContext } from '../../hooks/usePageContext'
import { BackgroundRippleEffect } from '../ui/background-ripple-effect'

export function AppShell() {
  usePageContext()

  return (
    <div
      className="relative flex flex-col h-screen w-screen overflow-hidden"
      style={{ background: 'linear-gradient(135deg, #1D4ED8 0%, #1a9e6e 50%, #3EE089 100%)' }}
    >
      {/* Ripple background — sits behind everything */}
      <BackgroundRippleEffect />

      {/* UI layer — sits on top */}
      <div className="relative z-10 flex flex-col h-full w-full">
        <Navbar />
        <ChatArea />
      </div>
    </div>
  )
}
