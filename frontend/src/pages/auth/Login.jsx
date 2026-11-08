
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, ShieldCheck, CreditCard } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

function Login() {
  const navigate = useNavigate()
  const { login } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')

    if (!email.trim() || !password) {
      setError('Please enter your email and password.')
      return
    }

    try {
      setLoading(true)
      await login({ email: email.trim(), password })
      navigate('/dashboard')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Login failed. Please check your credentials and try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-950 px-4 py-10 text-white">
      <div className="grid w-full max-w-5xl overflow-hidden rounded-3xl border border-slate-800 bg-slate-900 shadow-2xl md:grid-cols-2">

        {/* Left information panel */}
        <div className="hidden flex-col justify-between bg-gradient-to-br from-indigo-700 to-slate-900 p-10 md:flex">
          <div>
            <div className="flex items-center gap-3">
              <div className="rounded-xl bg-white/15 p-3">
                <CreditCard size={28} />
              </div>
              <span className="text-2xl font-bold tracking-wide">
                SMARTPAY
              </span>
            </div>

            <h1 className="mt-20 text-4xl font-bold leading-tight">
              Smarter Payments.
              <br />
              Safer Transactions.
            </h1>

            <p className="mt-5 leading-7 text-indigo-100">
              Manage simulated payments, monitor fraud risk
              and track webhook activity from one dashboard.
            </p>
          </div>

          <div className="flex items-center gap-3 text-sm text-indigo-100">
            <ShieldCheck size={20} />
            Secure JWT authentication
          </div>
        </div>

        {/* Login form */}
        <div className="p-7 sm:p-10">
          <div className="mb-8 md:hidden">
            <h1 className="text-2xl font-bold text-white">SMARTPAY</h1>
            <p className="mt-1 text-sm text-slate-400">
              Smart Payment & Fraud Detection
            </p>
          </div>

          <h2 className="text-3xl font-bold">Welcome back</h2>
          <p className="mt-2 text-sm text-slate-400">
            Sign in to access your SmartPay account.
          </p>

          {error && (
            <div
              role="alert"
              className="mt-6 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300"
            >
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-8 space-y-5">
            <div>
              <label
                htmlFor="email"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Email address
              </label>

              <input
                id="email"
                type="email"
                value={email}
                onChange={(event) => setEmail(event.target.value)}
                placeholder="you@example.com"
                autoComplete="email"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              />
            </div>

            <div>
              <label
                htmlFor="password"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Password
              </label>

              <div className="relative">
                <input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(event) => setPassword(event.target.value)}
                  placeholder="Enter your password"
                  autoComplete="current-password"
                  required
                  className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 pr-12 text-white outline-none transition placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
                />

                <button
                  type="button"
                  onClick={() => setShowPassword(!showPassword)}
                  aria-label={showPassword ? 'Hide password' : 'Show password'}
                  className="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 hover:text-white"
                >
                  {showPassword ? <EyeOff size={20} /> : <Eye size={20} />}
                </button>
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Signing in...' : 'Sign In'}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-400">
            Don't have an account?{' '}
            <Link
              to="/register"
              className="font-semibold text-indigo-400 hover:text-indigo-300"
            >
              Create account
            </Link>
          </p>

          <p className="mt-8 text-center text-xs text-slate-500">
            SMARTPAY · Development Environment
          </p>
        </div>
      </div>
    </div>
  )
}

export default Login
