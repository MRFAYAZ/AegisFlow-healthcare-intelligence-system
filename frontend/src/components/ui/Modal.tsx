import React from 'react'
interface ModalProps {
  open: boolean
  onClose: () => void
  title: string
  subtitle?: string
  children: React.ReactNode
  footer?: React.ReactNode
  width?: string
}
export function Modal({ open, onClose, title, subtitle, children, footer, width='480px' }: ModalProps) {
  if (!open) return null
  return (
    <div className="fixed inset-0 bg-black/40 z-50 flex items-center justify-center p-4" onClick={onClose}>
      <div className="bg-white border border-border rounded-xl shadow-lg overflow-y-auto max-h-[90vh]"
        style={{ width, maxWidth:'95vw' }}
        onClick={(e) => e.stopPropagation()}>
        <div className="flex items-start justify-between p-5 border-b border-border">
          <div>
            <div className="text-[14px] font-semibold text-ink">{title}</div>
            {subtitle && <div className="text-[11px] text-ink-faint mt-0.5">{subtitle}</div>}
          </div>
          <button onClick={onClose} className="w-6 h-6 rounded border border-border bg-surface-muted text-ink-muted hover:bg-surface-subtle flex items-center justify-center text-[13px]">✕</button>
        </div>
        <div className="p-5">{children}</div>
        {footer && <div className="flex gap-2 justify-end p-4 border-t border-border">{footer}</div>}
      </div>
    </div>
  )
}
