
import { useState } from 'react'
import { NavLink, useNavigate } from 'react-router-dom'
import { useAuth } from '../../context/AuthContext'

function DashboardLayout({ children }) {
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const { user, logout } = useAuth()
  const navigate = useNavigate()

  const handleLogout = () => {
    logout()
    navigate('/login')
  }

 const navItems = [
  { label: 'Overview', path: '/dashboard', icon: 'O' },
  { label: 'Create Payment', path: '/payments/create', icon: 'P' },
  { label: 'Verify Payment', path: '/payments/verify', icon: 'V' },
  { label: 'Payment History', path: '/payments/history', icon: 'H' },
  { label: 'Fraud Monitoring', path: '/fraud', icon: 'F' },
  { label: 'Webhooks', path: '/webhooks', icon: 'W' },
]

  const sidebarContent = (
    <>
      <div className="mb-10 flex items-center gap-3 px-2">
        <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-indigo-600 text-xl font-bold text-white">
          S
        </div>

        <div>
          <h1 className="text-xl font-bold text-white">SMARTPAY</h1>
          <p className="text-xs text-slate-400">Payment Platform</p>
        </div>
      </div>

      <p className="mb-3 px-3 text-xs font-semibold uppercase tracking-wider text-slate-500">
        Main Menu
      </p>

      <nav className="space-y-2">
        {navItems.map((item) =>
          item.soon ? (
            <div
              key={item.label}
              className="flex cursor-not-allowed items-center justify-between rounded-xl px-4 py-3 text-sm text-slate-500"
            >
              <span className="flex items-center gap-3">
                <span>{item.icon}</span>
                {item.label}
              </span>

              <span className="rounded-md bg-slate-800 px-2 py-1 text-xs">
                Soon
              </span>
            </div>
          ) : (
            <NavLink
              key={item.label}
              to={item.path}
              onClick={() => setMobileMenuOpen(false)}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-xl px-4 py-3 text-sm font-medium transition ${
                  isActive
                    ? 'bg-indigo-600 text-white'
                    : 'text-slate-400 hover:bg-slate-800 hover:text-white'
                }`
              }
            >
              <span>{item.icon}</span>
              {item.label}
            </NavLink>
          ),
        )}
      </nav>

      <div className="mt-auto border-t border-slate-800 pt-6">
        <p className="truncate px-3 text-sm text-slate-300">
          {user?.email || 'User'}
        </p>

        <p className="px-3 pt-1 text-xs capitalize text-slate-500">
          {user?.role || 'Customer'}
        </p>

        <button
          onClick={handleLogout}
          className="mt-4 w-full rounded-xl px-4 py-3 text-left text-sm text-red-400 transition hover:bg-slate-800"
        >
          Sign Out
        </button>
      </div>
    </>
  )

  return (
    <div className="min-h-screen bg-slate-950 text-white">
      <aside className="fixed inset-y-0 left-0 z-30 hidden w-64 flex-col border-r border-slate-800 bg-slate-900 p-6 lg:flex">
        {sidebarContent}
      </aside>

      {mobileMenuOpen && (
        <div
          className="fixed inset-0 z-40 bg-black/60 lg:hidden"
          onClick={() => setMobileMenuOpen(false)}
        >
          <aside
            className="flex h-full w-72 flex-col bg-slate-900 p-6"
            onClick={(event) => event.stopPropagation()}
          >
            {sidebarContent}
          </aside>
        </div>
      )}

      <div className="min-h-screen lg:pl-64">
        <header className="flex items-center justify-between border-b border-slate-800 bg-slate-900/70 px-6 py-4">
          <button
            onClick={() => setMobileMenuOpen(true)}
            className="rounded-lg px-3 py-2 text-slate-300 hover:bg-slate-800 lg:hidden"
            aria-label="Open navigation menu"
          >
            Menu
          </button>

          <span className="text-sm font-medium text-slate-300">
            SmartPay Dashboard
          </span>

          <span className="text-xs text-indigo-300">Development</span>
        </header>

        <main className="p-5 sm:p-8">{children}</main>
      </div>
    </div>
  )
}

export default DashboardLayout
