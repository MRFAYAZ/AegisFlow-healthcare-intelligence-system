import React from 'react'
interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary'|'red'|'orange'|'green'|'ghost'
  size?: 'sm'|'md'
  children: React.ReactNode
}
export function Button({ variant='primary', size='md', children, className='', type='button', ...props }: ButtonProps) {
  const sizes = { sm:'text-[11px] px-2.5 py-1', md:'text-[12px] px-3 py-1.5' }
  return (
    <button type={type} aria-disabled={props.disabled || undefined} className={`btn btn-${variant} ${sizes[size]} ${className}`} {...props}>
      {children}
    </button>
  )
}
