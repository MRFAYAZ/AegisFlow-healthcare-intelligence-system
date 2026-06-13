interface BadgeProps {
  variant: 'red'|'orange'|'yellow'|'green'|'blue'
  children: React.ReactNode
  pulse?: boolean
}
export function Badge({ variant, children, pulse }: BadgeProps) {
  return (
    <span className={`badge badge-${variant}${pulse ? ' pulse' : ''}`}>
      {children}
    </span>
  )
}
