import { Toaster } from 'sonner'
export function ToastProvider() {
  return (
    <Toaster
      position="bottom-right"
      toastOptions={{
        style: {
          background: '#ffffff',
          border: '1px solid #e5e3de',
          color: '#1a1916',
          fontSize: '12px',
          borderRadius: '10px',
          boxShadow: '0 2px 12px rgba(0,0,0,0.08)',
        },
      }}
    />
  )
}
