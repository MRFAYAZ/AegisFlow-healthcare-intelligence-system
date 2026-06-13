import { Button } from './Button'
interface Props { count: number; onView: () => void }
export function EmergencyBanner({ count, onView }: Props) {
  if (count === 0) return (
    <div className="bg-green-50 border border-green-200 rounded-lg p-3 mb-4 flex items-center gap-3">
      <div className="w-7 h-7 rounded bg-green-100 flex items-center justify-center text-green-600 text-sm flex-shrink-0">✓</div>
      <div className="flex-1"><div className="text-[13px] font-semibold text-green-800">All systems normal — no active emergencies</div></div>
    </div>
  )
  return (
    <div className="emer-banner">
      <div className="w-7 h-7 rounded bg-red-200 flex items-center justify-center text-status-red text-sm flex-shrink-0 flex-shrink-0">!</div>
      <div className="flex-1">
        <div className="text-[13px] font-semibold text-red-800">{count} active emergency shortage{count>1?'s':''}</div>
        <div className="text-[11px] text-red-700 mt-0.5">Immediate redistribution required · AI engine active</div>
      </div>
      <Button variant="red" size="sm" onClick={onView}>View all →</Button>
    </div>
  )
}