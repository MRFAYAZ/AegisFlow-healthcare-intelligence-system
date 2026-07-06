import { useRouteError, isRouteErrorResponse } from "react-router-dom"

export function RouteErrorPage() {
  const error = useRouteError()

  const message = isRouteErrorResponse(error)
    ? error.statusText || error.data?.message || "An unexpected error occurred."
    : error instanceof Error
      ? error.message
      : "An unexpected error occurred."

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6 py-12">
      <div className="w-full max-w-md rounded-2xl border border-slate-200 bg-white p-8 text-center shadow-sm">
        <div className="mx-auto flex h-12 w-12 items-center justify-center rounded-full bg-amber-100 text-xl text-amber-700">
          !
        </div>
        <h1 className="mt-4 text-xl font-semibold text-slate-900">Something went wrong</h1>
        <p className="mt-2 text-sm text-slate-600">The application hit an unexpected issue. Please refresh the page or return to the dashboard.</p>
        <p className="mt-4 rounded-xl bg-slate-50 px-3 py-2 text-sm text-slate-500">{message}</p>
        <button
          type="button"
          onClick={() => window.location.reload()}
          className="mt-6 rounded-full bg-slate-900 px-4 py-2 text-sm font-medium text-white"
        >
          Reload page
        </button>
      </div>
    </div>
  )
}
