import { KBPanel } from '../sidebar/KBPanel'

export function Sidebar() {
  return (
    <div className="w-72 shrink-0 flex flex-col h-full bg-james-surface border-r border-james-border overflow-y-auto">
      {/* Header */}
      <div className="px-5 py-5 border-b border-james-border">
        <div className="flex items-center gap-2">
          <div className="w-7 h-7 rounded-lg bg-gradient-to-br from-james-primary to-james-teal flex items-center justify-center">
            <span className="text-white text-xs font-bold">J</span>
          </div>
          <div>
            <p className="text-james-text text-sm font-semibold leading-none">James AI</p>
            <p className="text-james-muted text-xs mt-0.5">by BondScanner</p>
          </div>
        </div>
      </div>

      {/* KB Panel */}
      <div className="flex-1 px-4 py-5">
        <KBPanel />
      </div>

      {/* Footer */}
      <div className="px-5 py-3 border-t border-james-border">
        <p className="text-james-muted/50 text-xs text-center">PoC v0.1 · Internal only</p>
      </div>
    </div>
  )
}
