
import { useState } from 'react'
import { Link, useNavigate } from 'react-router-dom'
import { Eye, EyeOff, ShieldCheck, UserPlus } from 'lucide-react'
import { useAuth } from '../../context/AuthContext'

function Register() {
  const navigate = useNavigate()
  const { register } = useAuth()

  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [confirmPassword, setConfirmPassword] = useState('')
  const [showPassword, setShowPassword] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [loading, setLoading] = useState(false)

  async function handleSubmit(event) {
    event.preventDefault()
    setError('')
    setSuccess('')

    if (password.length < 8) {
      setError('Password must contain at least 8 characters.')
      return
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.')
      return
    }

    try {
      setLoading(true)

      await register({
        email: email.trim(),
        password,
      })

      setSuccess('Account created successfully! Redirecting to login...')

      setTimeout(() => {
        navigate('/login')
      }, 1500)
    } catch (err) {
      setError(
        err.response?.data?.detail ||
        'Registration failed. Please try again.',
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
                <ShieldCheck size={28} />
              </div>
              <span className="text-2xl font-bold tracking-wide">
                SMARTPAY
              </span>
            </div>

            <h1 className="mt-20 text-4xl font-bold leading-tight">
              Start Your
              <br />
              Secure Payment Journey.
            </h1>

            <p className="mt-5 leading-7 text-indigo-100">
              Create an account to explore payment simulation,
              fraud detection and transaction monitoring.
            </p>
          </div>

          <div className="flex items-center gap-3 text-sm text-indigo-100">
            <ShieldCheck size={20} />
            JWT-based account authentication
          </div>
        </div>

        {/* Registration form */}
        <div className="p-7 sm:p-10">
          <div className="mb-8 md:hidden">
            <h1 className="text-2xl font-bold">SMARTPAY</h1>
            <p className="mt-1 text-sm text-slate-400">
              Smart Payment & Fraud Detection
            </p>
          </div>

          <div className="mb-5 inline-flex rounded-xl bg-indigo-500/10 p-3 text-indigo-400">
            <UserPlus size={26} />
          </div>

          <h2 className="text-3xl font-bold">Create account</h2>
          <p className="mt-2 text-sm text-slate-400">
            Register to get started with SmartPay.
          </p>

          {error && (
            <div
              role="alert"
              className="mt-6 rounded-lg border border-red-500/30 bg-red-500/10 p-3 text-sm text-red-300"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              role="status"
              className="mt-6 rounded-lg border border-emerald-500/30 bg-emerald-500/10 p-3 text-sm text-emerald-300"
            >
              {success}
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
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
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
                  placeholder="Create a password"
                  autoComplete="new-password"
                  required
                  className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 pr-12 text-white outline-none placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
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

              <p className="mt-2 text-xs text-slate-500">
                Use at least 8 characters.
              </p>
            </div>

            <div>
              <label
                htmlFor="confirmPassword"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Confirm password
              </label>

              <input
                id="confirmPassword"
                type="password"
                value={confirmPassword}
                onChange={(event) => setConfirmPassword(event.target.value)}
                placeholder="Enter your password again"
                autoComplete="new-password"
                required
                className="w-full rounded-xl border border-slate-700 bg-slate-800 px-4 py-3 text-white outline-none placeholder:text-slate-500 focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-indigo-600 px-4 py-3 font-semibold transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {loading ? 'Creating account...' : 'Create Account'}
            </button>
          </form>

          <p className="mt-8 text-center text-sm text-slate-400">
            Already have an account?{' '}
            <Link
              to="/login"
              className="font-semibold text-indigo-400 hover:text-indigo-300"
            >
              Sign in
            </Link>
          </p>

          <p className="mt-8 text-center text-xs text-slate-500">
            SMARTPAY - Development Environment
          </p>
        </div>
      </div>
    </div>
  )
}

export default Register
