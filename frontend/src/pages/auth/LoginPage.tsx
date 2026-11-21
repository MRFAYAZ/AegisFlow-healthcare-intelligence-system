import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { authAPI } from '../../services/api'
import { useAppStore } from '../../store/useAppStore'

function decodeJwtRole(token: string): string | null {
  try {
    const payload = token.split('.')[1]
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized.padEnd(Math.ceil(normalized.length / 4) * 4, '=')
    const decoded = JSON.parse(atob(padded))
    return typeof decoded?.role === 'string' ? decoded.role.toLowerCase() : null
  } catch {
    return null
  }
}

const DEMO_USERS = [
  {
    name: 'System Admin',
    email: 'admin@aegisflow.com',
    password: 'Admin@123',
    role: 'system_admin',
    profile: 'SYSTEM_ADMIN',
    facility: 'AegisFlow HQ',
    profile_access: ['dashboard', 'emergency', 'inventory', 'shortage', 'transfers', 'dispatcher', 'analytics', 'map', 'shop', 'procurement', 'network_exchange', 'profiles']
  },
  {
    name: 'Hospital Admin',
    email: 'hospital@aegisflow.com',
    password: 'Hospital@123',
    role: 'hospital_admin',
    profile: 'HOSPITAL_ADMIN',
    facility: 'City General Hospital',
    profile_access: ['dashboard', 'emergency', 'inventory', 'shortage', 'transfers', 'procurement', 'analytics', 'map', 'network_exchange', 'profiles']
  },
  {
    name: 'Emergency Operator',
    email: 'emergency@aegisflow.com',
    password: 'Emergency@123',
    role: 'emergency_operator',
    profile: 'EMERGENCY_OPERATOR',
    facility: 'Operations Center',
    profile_access: ['dashboard', 'emergency', 'shortage', 'transfers', 'dispatcher', 'analytics', 'map', 'procurement', 'network_exchange']
  },
  {
    name: 'Supplier Manager',
    email: 'supplier@aegisflow.com',
    password: 'Supplier@123',
    role: 'supplier_manager',
    profile: 'SUPPLIER_MANAGER',
    facility: 'North Supply Hub',
    profile_access: ['dashboard', 'inventory', 'shortage', 'procurement', 'transfers', 'analytics', 'map', 'network_exchange']
  }
]

export function LoginPage() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)

  const { setUser } = useAppStore()

  const navigate = useNavigate()

  async function handleLogin(
    e: React.FormEvent
  ) {
    e.preventDefault()

    setLoading(true)

    try {
      const demoUser = DEMO_USERS.find(
        (entry) => entry.email.toLowerCase() === email.toLowerCase().trim() && entry.password === password
      )

      let accessToken = ''
      let userRole: string | null = null
      let profileName: string | undefined
      let profileAccess: string[] | undefined

      try {
        const response = await authAPI.login(email, password)
        accessToken = response?.data?.access_token ?? ''
        userRole = decodeJwtRole(accessToken)
      } catch (error) {
        console.warn('Backend login unavailable, trying local demo fallback.', error)
      }

      if (!accessToken && demoUser) {
        accessToken = `demo-token-${demoUser.role}`
        userRole = demoUser.role
        profileName = demoUser.profile
        profileAccess = demoUser.profile_access
      }

      if (!accessToken) {
        throw new Error('Invalid credentials')
      }

      localStorage.setItem('aegisflow_token', accessToken)

      if (!accessToken.startsWith('demo-token-')) {
        try {
          const meResponse = await authAPI.me()
          const backendRole = meResponse?.data?.role
          const backendProfile = meResponse?.data?.profile
          const backendProfileAccess = meResponse?.data?.profile_access
          if (backendRole) {
            userRole = String(backendRole).toLowerCase()
          }
          if (backendProfile) {
            profileName = String(backendProfile)
          }
          if (backendProfileAccess) {
            profileAccess = backendProfileAccess
          }
        } catch (profileError) {
          console.warn('Could not load current user profile, using fallback profile data.', profileError)
        }
      }

      const fallbackProfileAccess = userRole
        ? DEMO_USERS.find((demo) => demo.role === userRole)?.profile_access ?? []
        : []

      const signedInUser = {
        id: 'authenticated-user',
        name: demoUser?.name ?? email,
        email,
        role: userRole ?? demoUser?.role ?? 'hospital_admin',
        profile: profileName ?? demoUser?.profile ?? userRole ?? 'HOSPITAL_ADMIN',
        profile_access: profileAccess ?? fallbackProfileAccess,
        facility: demoUser?.facility ?? 'AegisFlow HQ'
      }

      setUser(signedInUser)

      toast.success('Login successful')
      navigate('/dashboard')
    } catch (error) {
      console.error(error)
      toast.error('Invalid credentials')
    } finally {
      setLoading(false)
    }
  }

  function quickLogin(
    user: typeof DEMO_USERS[0]
  ) {

    setEmail(user.email)

    setPassword(user.password)

  }

  return (
    <div className="min-h-screen bg-surface-bg flex items-center justify-center p-4">
      <div className="w-full max-w-sm">

        {/* Logo */}
        <div className="flex items-center gap-3 mb-8 justify-center">
          <div className="w-10 h-10 bg-blue-700 rounded-xl flex items-center justify-center">
            <span className="text-white text-lg font-bold">
              A
            </span>
          </div>

          <div>
            <div className="text-[18px] font-semibold text-ink">
              AegisFlow
            </div>

            <div className="text-[11px] text-ink-faint">
              Healthcare Intelligence Platform
            </div>
          </div>
        </div>

        {/* Card */}
        <div className="bg-white border border-border rounded-xl p-6 shadow-sm">

          <div className="mb-5">
            <div className="text-[15px] font-semibold text-ink mb-1">
              Sign in
            </div>

            <div className="text-[12px] text-ink-faint">
              Access your healthcare dashboard
            </div>
          </div>

          <form onSubmit={handleLogin}>

            <div className="mb-3">
              <label className="f-label">
                Email address
              </label>

              <input
                className="f-input"
                type="email"
                value={email}
                onChange={(e) =>
                  setEmail(
                    e.target.value
                  )
                }
                placeholder="you@hospital.in"
                required
              />
            </div>

            <div className="mb-5">
              <label className="f-label">
                Password
              </label>

              <input
                className="f-input"
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(
                    e.target.value
                  )
                }
                placeholder="••••••••"
                required
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full btn btn-primary py-2.5 justify-center text-[13px] font-medium disabled:opacity-60"
            >
              {loading
                ? 'Signing in...'
                : 'Sign in'}
            </button>

          </form>

          {/* Demo Quick Login */}
          <div className="mt-5 pt-4 border-t border-border">

            <div className="text-[10px] text-ink-faint uppercase tracking-[0.5px] mb-2">
              Quick demo login
            </div>

            <div className="flex flex-col gap-1.5">

              {DEMO_USERS.map(
                (user) => (
                  <button
                    key={user.email}
                    onClick={() =>
                      quickLogin(user)
                    }
                    className="text-left px-3 py-2 rounded border border-border hover:bg-surface-muted text-[11px] text-ink-muted hover:text-ink transition-colors"
                  >
                    <span className="font-medium text-ink">
                      {user.name}
                    </span>

                    <span className="text-ink-faint ml-1">
                      · {user.role.replace(
                        '_',
                        ' '
                      )}
                    </span>
                  </button>
                )
              )}

            </div>

          </div>

        </div>

        <div className="text-center mt-4 text-[11px] text-ink-faint">
          Predict · Alert · Redistribute · Heal
        </div>

      </div>
    </div>
  )
}