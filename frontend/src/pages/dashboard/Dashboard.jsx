
import { ShieldCheck, CreditCard, Activity } from 'lucide-react'
import DashboardLayout from '../../components/layout/DashboardLayout'

function Dashboard() {
  return (
    <DashboardLayout>
      <div>
        <div>
          <h1 className="text-3xl font-bold">Dashboard Overview</h1>
          <p className="mt-2 text-sm text-slate-400">
            Welcome to your SmartPay payment management workspace.
          </p>
        </div>

        <div className="mt-8 rounded-2xl border border-emerald-500/20 bg-emerald-500/5 p-5">
          <div className="flex items-center gap-3">
            <ShieldCheck className="text-emerald-400" size={24} />
            <div>
              <h2 className="font-semibold text-emerald-400">
                Authentication Protected
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                You have successfully accessed the protected dashboard.
              </p>
            </div>
          </div>
        </div>

        <div className="mt-8 grid gap-5 md:grid-cols-2 xl:grid-cols-3">
          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <CreditCard className="text-indigo-400" size={25} />
            <h3 className="mt-5 font-semibold">Payment Management</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Create and verify simulated payment transactions.
            </p>
            <p className="mt-4 text-xs text-slate-500">
              Payment module coming next
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <ShieldCheck className="text-emerald-400" size={25} />
            <h3 className="mt-5 font-semibold">Fraud Detection</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Review transaction risk scores and risk levels.
            </p>
            <p className="mt-4 text-xs text-slate-500">
              Fraud module coming soon
            </p>
          </div>

          <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
            <Activity className="text-purple-400" size={25} />
            <h3 className="mt-5 font-semibold">Webhook Monitoring</h3>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Manage webhook endpoints and delivery attempts.
            </p>
            <p className="mt-4 text-xs text-slate-500">
              Webhook module coming soon
            </p>
          </div>
        </div>

        <div className="mt-8 rounded-2xl border border-slate-800 bg-slate-900 p-6">
          <h2 className="font-semibold">System Information</h2>
          <p className="mt-3 text-sm text-slate-400">
            SmartPay is an educational payment processing and fraud
            detection simulation. No real bank transactions are processed.
          </p>
        </div>
      </div>
    </DashboardLayout>
  )
}

export default Dashboard
