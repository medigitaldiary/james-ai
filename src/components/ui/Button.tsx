import { type ReactNode, type ButtonHTMLAttributes } from 'react'
import { Spinner } from './Spinner'

type Variant = 'primary' | 'ghost' | 'danger'

interface Props extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: Variant
  isLoading?: boolean
  children: ReactNode
}

const variantClasses: Record<Variant, string> = {
  primary:
    'bg-james-primary hover:bg-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed',
  ghost:
    'border border-james-border text-james-muted hover:text-james-text hover:border-james-teal transition-colors',
  danger:
    'text-red-400 hover:text-red-300 hover:bg-red-400/10 transition-colors',
}

export function Button({
  variant = 'primary',
  isLoading,
  children,
  className = '',
  ...props
}: Props) {
  return (
    <button
      className={`flex items-center justify-center gap-2 rounded-lg px-3 py-2 text-sm font-medium transition-all ${variantClasses[variant]} ${className}`}
      disabled={isLoading || props.disabled}
      {...props}
    >
      {isLoading ? <Spinner size={14} /> : children}
    </button>
  )
}
