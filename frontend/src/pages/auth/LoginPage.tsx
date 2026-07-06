import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { toast } from 'sonner'

import { authAPI } from '../../services/api'
import { useAppStore } from '../../store/useAppStore'

const DEMO_USERS = [
  {
    name: 'System Admin',
    email: 'admin@aegisflow.com',
    password: 'Admin@123',
    role: 'system_admin',
    facility: 'AegisFlow HQ'
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

      const response = await authAPI.login(
        email,
        password
      )

      const token =
        response.data.access_token

      localStorage.setItem(
        'aegisflow_token',
        token
      )

      setUser({
        id: 'authenticated-user',
        name: email,
        email,
        role: 'system_admin'
      })

      toast.success(
        'Login successful'
      )

      navigate('/dashboard')

    } catch (error) {

      console.error(error)

      toast.error(
        'Invalid credentials'
      )

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