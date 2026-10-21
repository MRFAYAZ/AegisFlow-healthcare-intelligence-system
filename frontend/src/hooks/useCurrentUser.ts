import { useQuery } from "@tanstack/react-query"
import { authAPI } from "../services/api"
import type { User } from "../types"

interface BackendCurrentUser {
  user_id: string
  full_name: string
  email: string
  role: string
  facility_ids: string[]
}

function normalizeRole(role: string): string {
  const normalized = role.toUpperCase()
  if (normalized === "SUPPLIER_MANAGER") return "supplier"
  return normalized.toLowerCase()
}

export function useCurrentUser() {
  const hasToken = Boolean(localStorage.getItem("aegisflow_token"))
  return useQuery<User | null>({
    queryKey: ["current-user"],
    enabled: hasToken,
    retry: false,
    staleTime: 60_000,
    queryFn: async () => {
      const response = await authAPI.me()
      const user = response.data as BackendCurrentUser
      return {
        id: user.user_id,
        name: user.full_name,
        email: user.email,
        role: normalizeRole(user.role),
        facilityIds: user.facility_ids ?? [],
      }
    },
  })
}
