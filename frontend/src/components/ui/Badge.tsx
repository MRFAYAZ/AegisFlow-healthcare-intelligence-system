interface BadgeProps {
  variant: 'red'|'orange'|'yellow'|'green'|'blue'
  children: React.ReactNode
  pulse?: boolean
  className?: string
}
export function Badge({ variant, children, pulse, className }: BadgeProps) {
  return (
    <span className={`badge badge-${variant}${pulse ? ' pulse' : ''} ${className ?? ''}`}>
      {children}
    </span>
  )
}
