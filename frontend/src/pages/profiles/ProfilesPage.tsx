import { useEffect, useState } from 'react'
import { ShieldCheck, Lock, Users, Sparkles } from 'lucide-react'
import { profilesAPI } from '../../services/api'

interface ProfileSummary {
  profile_code: string
  profile_name: string
  module_access: string[]
  is_default: boolean
  is_active: boolean
}

const fallbackProfiles: ProfileSummary[] = [
  {
    profile_code: 'SYSTEM_ADMIN',
    profile_name: 'System administrator',
    module_access: ['dashboard', 'emergency', 'inventory', 'shortage', 'transfers', 'dispatcher', 'analytics', 'map', 'shop', 'procurement', 'network_exchange', 'profiles'],
    is_default: false,
    is_active: true,
  },
  {
    profile_code: 'HOSPITAL_ADMIN',
    profile_name: 'Hospital administrator',
    module_access: ['dashboard', 'emergency', 'inventory', 'shortage', 'transfers', 'procurement', 'analytics', 'map', 'network_exchange', 'profiles'],
    is_default: true,
    is_active: true,
  },
  {
    profile_code: 'PHARMACIST',
    profile_name: 'Pharmacist',
    module_access: ['dashboard', 'inventory', 'shortage', 'transfers', 'shop', 'network_exchange'],
    is_default: false,
    is_active: true,
  },
  {
    profile_code: 'EMERGENCY_OPERATOR',
    profile_name: 'Emergency operator',
    module_access: ['dashboard', 'emergency', 'shortage', 'transfers', 'dispatcher', 'analytics', 'map', 'procurement', 'network_exchange'],
    is_default: false,
    is_active: true,
  },
  {
    profile_code: 'SUPPLIER_MANAGER',
    profile_name: 'Supplier manager',
    module_access: ['dashboard', 'inventory', 'shortage', 'procurement', 'transfers', 'analytics', 'map', 'network_exchange'],
    is_default: false,
    is_active: true,
  },
]

const moduleDisplay: Record<string, string> = {
  dashboard: 'Dashboard',
  emergency: 'Emergency',
  inventory: 'Inventory',
  shortage: 'Shortage',
  transfers: 'Transfers',
  dispatcher: 'Dispatch',
  analytics: 'Analytics',
  map: 'Map',
  shop: 'Shop',
  procurement: 'Procurement',
  network_exchange: 'Network exchange',
  profiles: 'Profiles',
}

export function ProfilesPage() {
  const [profiles, setProfiles] = useState<ProfileSummary[]>(fallbackProfiles)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    profilesAPI.getAll()
      .then((response) => {
        setProfiles(response.data ?? fallbackProfiles)
      })
      .catch(() => {
        setProfiles(fallbackProfiles)
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-semibold text-ink">Access profiles</h1>
          <p className="text-sm text-ink-faint mt-1">Govern role and module boundaries to keep the network coordination layer secure and auditable.</p>
        </div>
        <div className="flex items-center gap-2 rounded-full border border-blue-200 bg-blue-50 px-3 py-1.5 text-xs font-semibold text-blue-700">
          <ShieldCheck size={14} />
          Policy-aware access
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-xl border border-border bg-white p-4">
          <div className="flex items-center gap-2 text-ink text-sm font-semibold">
            <Users size={16} />
            Profiles
          </div>
          <div className="mt-3 text-3xl font-semibold text-ink">{profiles.length}</div>
          <div className="text-xs text-ink-faint">Defined access roles</div>
        </div>

        <div className="rounded-xl border border-border bg-white p-4">
          <div className="flex items-center gap-2 text-ink text-sm font-semibold">
            <Lock size={16} />
            Security model
          </div>
          <div className="mt-3 text-3xl font-semibold text-ink">RBAC + ABAC</div>
          <div className="text-xs text-ink-faint">Role and module restrictions</div>
        </div>

        <div className="rounded-xl border border-border bg-white p-4">
          <div className="flex items-center gap-2 text-ink text-sm font-semibold">
            <Sparkles size={16} />
            Compliance
          </div>
          <div className="mt-3 text-3xl font-semibold text-ink">Audit-ready</div>
          <div className="text-xs text-ink-faint">Every access boundary is tracked</div>
        </div>
      </div>

      <div className="grid gap-4 xl:grid-cols-2">
        {loading ? (
          <div className="rounded-xl border border-border bg-white p-6 text-sm text-ink-faint">Loading profile matrix…</div>
        ) : (
          profiles.map((profile) => (
            <div key={profile.profile_code} className="rounded-xl border border-border bg-white p-5">
              <div className="flex items-center justify-between gap-3">
                <div>
                  <div className="text-sm font-semibold text-ink">{profile.profile_name}</div>
                  <div className="text-xs text-ink-faint uppercase tracking-[0.08em]">{profile.profile_code}</div>
                </div>
                <div className="flex items-center gap-2">
                  {profile.is_default && (
                    <span className="rounded-full border border-blue-200 bg-blue-50 px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] text-blue-700">
                      Default
                    </span>
                  )}
                  <span className={`rounded-full px-2 py-1 text-[10px] font-semibold uppercase tracking-[0.08em] ${profile.is_active ? 'border border-green-200 bg-green-50 text-green-700' : 'border border-gray-200 bg-gray-50 text-gray-600'}`}>
                    {profile.is_active ? 'Active' : 'Inactive'}
                  </span>
                </div>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {profile.module_access.map((module) => (
                  <span key={`${profile.profile_code}-${module}`} className="rounded-full border border-border bg-surface-muted px-2.5 py-1 text-[11px] font-medium text-ink">
                    {moduleDisplay[module] ?? module.replace(/_/g, ' ')}
                  </span>
                ))}
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
