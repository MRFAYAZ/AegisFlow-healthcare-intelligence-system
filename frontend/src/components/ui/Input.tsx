import React from 'react'
interface InputProps extends React.InputHTMLAttributes<HTMLInputElement> {
  label?: string
}
export function Input({ label, className='', ...props }: InputProps) {
  return (
    <div className="mb-3">
      {label && <label className="f-label">{label}</label>}
      <input className={`f-input ${className}`} {...props} />
    </div>
  )
}
interface SelectProps extends React.SelectHTMLAttributes<HTMLSelectElement> {
  label?: string
  options: { value: string; label: string }[]
}
export function Select({ label, options, className='', ...props }: SelectProps) {
  return (
    <div className="mb-3">
      {label && <label className="f-label">{label}</label>}
      <select className={`f-input ${className}`} {...props}>
        {options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
      </select>
    </div>
  )
}
