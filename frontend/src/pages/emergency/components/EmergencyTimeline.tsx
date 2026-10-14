import { useQuery } from "@tanstack/react-query"
import { emergencyAPI } from "../../../services/api"
import type { Emergency } from "../../../types/emergency"
import { useCurrentUser } from "../../../hooks/useCurrentUser"

interface TimelineEvent {
  timestamp: string
  event_type: string
  title: string
  detail: string
  transfer_id: string | null
  timeline_event_id?: string | null
  actor_user_id?: string | null
  event_payload?: Record<string, unknown>
  event_source?: "APPEND_ONLY_EVENT" | "LEGACY_TIMESTAMP"
}

interface TimelineResponse {
  emergency_case_id: string
  timeline_scope: string
  events: TimelineEvent[]
}

interface Props {
  emergency: Emergency
}

export function EmergencyTimeline({ emergency }: Props) {
  const { data: user } = useCurrentUser()
  const { data, isLoading, isError, error } = useQuery<TimelineResponse>({
    queryKey: ["emergency-timeline", user?.id ?? "anonymous", emergency.emergency_case_id],
    queryFn: async () => {
      const response = await emergencyAPI.getTimeline(emergency.emergency_case_id)
      return response.data
    },
    enabled: Boolean(user?.id && emergency.emergency_case_id),
    refetchInterval: 10_000,
  })

  return (
    <section className="rounded-xl border border-slate-200 bg-white p-5">
      <div className="mb-4">
        <h3 className="text-lg font-semibold text-slate-900">Recorded operational timeline</h3>
        <p className="mt-1 text-sm text-slate-500">
          Recorded state transitions are stored as operational events; pre-upgrade records use their existing timestamps for any missing milestones.
        </p>
      </div>

      <div className="mb-4 rounded-lg border border-amber-200 bg-amber-50 p-3 text-xs text-amber-900">
        Newly recorded request, decision, dispatch and delivery actions are appended in the same transaction as their state change. Legacy events are labelled where only a timestamp was available.
      </div>

      {isLoading && (
        <div className="rounded-lg bg-slate-50 p-4 text-sm text-slate-500">
          Loading recorded milestones…
        </div>
      )}

      {isError && (
        <div role="alert" className="rounded-lg border border-red-200 bg-red-50 p-4 text-sm text-red-800">
          The timeline could not be loaded. {(error as Error).message}
        </div>
      )}

      {!isLoading && !isError && data?.events.length === 0 && (
        <div className="rounded-lg border border-dashed border-slate-300 p-5 text-center text-sm text-slate-500">
          No recorded milestones were returned for this emergency.
        </div>
      )}

      {!isLoading && !isError && (data?.events.length ?? 0) > 0 && (
        <ol className="space-y-4">
          {data!.events.map((event, index) => (
            <li key={`${event.timestamp}-${event.event_type}-${event.transfer_id ?? "emergency"}`} className="flex gap-3">
              <div className="flex flex-col items-center">
                <div className="flex h-7 w-7 items-center justify-center rounded-full bg-slate-900 text-xs font-semibold text-white">
                  {index + 1}
                </div>
                {index < data!.events.length - 1 && <div className="mt-1 min-h-6 w-px flex-1 bg-slate-200" />}
              </div>
              <div className="min-w-0 flex-1 rounded-lg border border-slate-200 p-3">
                <div className="flex flex-wrap items-start justify-between gap-2">
                  <p className="font-medium text-slate-900">{event.title}</p>
                  <time className="text-xs text-slate-500" dateTime={event.timestamp}>
                    {new Date(event.timestamp).toLocaleString()}
                  </time>
                </div>
                <p className="mt-1 text-sm text-slate-600">{event.detail}</p>
                {event.transfer_id && (
                  <p className="mt-2 text-xs text-slate-400">
                    Transfer #{event.transfer_id.slice(0, 8)}
                  </p>
                )}
                <div className="mt-2 flex flex-wrap items-center gap-2 text-[10px] text-slate-400">
                  {event.event_source === "APPEND_ONLY_EVENT"
                    ? <span className="rounded bg-emerald-50 px-2 py-1 text-emerald-700">Recorded event</span>
                    : <span className="rounded bg-slate-100 px-2 py-1 text-slate-600">Legacy timestamp</span>}
                  {event.actor_user_id && <span>Actor {event.actor_user_id.slice(0, 8)}</span>}
                  {event.timeline_event_id && <span>Event {event.timeline_event_id.slice(0, 8)}</span>}
                </div>
              </div>
            </li>
          ))}
        </ol>
      )}

      <p className="mt-4 text-xs text-slate-400">
        {data?.timeline_scope ?? "Timeline source: emergency, transfer and dispatch records."}
      </p>
    </section>
  )
}
