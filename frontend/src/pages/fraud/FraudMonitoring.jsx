
import { useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { getPaymentHistory } from '../../services/paymentHistoryService'

const filters = ['ALL', 'HIGH', 'MEDIUM', 'LOW']

function FraudMonitoring() {
  const [payments] = useState(() => getPaymentHistory())
  const [activeFilter, setActiveFilter] = useState('ALL')
  const [search, setSearch] = useState('')

  const getRiskLevel = (payment) => {
    const risk = String(payment.risk_level || '').toUpperCase()

    if (['HIGH', 'MEDIUM', 'LOW'].includes(risk)) {
      return risk
    }

    return 'UNKNOWN'
  }

  const stats = useMemo(() => {
    const high = payments.filter(
      (payment) => getRiskLevel(payment) === 'HIGH',
    ).length

    const medium = payments.filter(
      (payment) => getRiskLevel(payment) === 'MEDIUM',
    ).length

    const low = payments.filter(
      (payment) => getRiskLevel(payment) === 'LOW',
    ).length

    const totalScore = payments.reduce(
      (sum, payment) => sum + Number(payment.fraud_score || 0),
      0,
    )

    return {
      total: payments.length,
      high,
      medium,
      low,
      average: payments.length
        ? Math.round(totalScore / payments.length)
        : 0,
    }
  }, [payments])

  const filteredPayments = payments.filter((payment) => {
    const matchesRisk =
      activeFilter === 'ALL' || getRiskLevel(payment) === activeFilter

    const searchText = search.trim().toLowerCase()

    const matchesSearch =
      !searchText ||
      String(payment.id).includes(searchText) ||
      String(payment.transaction_id || '')
        .toLowerCase()
        .includes(searchText)

    return matchesRisk && matchesSearch
  })

  const riskStyles = {
    HIGH: 'bg-red-500/10 text-red-400 border-red-500/20',
    MEDIUM: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    LOW: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    UNKNOWN: 'bg-slate-500/10 text-slate-400 border-slate-500/20',
  }

  const statCards = [
    {
      label: 'Total Transactions',
      value: stats.total,
      description: 'Recorded in this browser',
      color: 'text-white',
    },
    {
      label: 'High Risk',
      value: stats.high,
      description: 'Requires attention',
      color: 'text-red-400',
    },
    {
      label: 'Medium Risk',
      value: stats.medium,
      description: 'Review recommended',
      color: 'text-amber-400',
    },
    {
      label: 'Low Risk',
      value: stats.low,
      description: 'Lower detected risk',
      color: 'text-emerald-400',
    },
  ]

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      <div>
        <p className="text-sm font-medium text-indigo-400">
          SECURITY & RISK MANAGEMENT
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Fraud Monitoring
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Monitor transaction risk scores and identify suspicious payments.
        </p>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {statCards.map((card) => (
          <div
            key={card.label}
            className="rounded-2xl border border-slate-800 bg-slate-900 p-5"
          >
            <p className="text-sm text-slate-400">{card.label}</p>

            <p className={`mt-3 text-3xl font-bold ${card.color}`}>
              {card.value}
            </p>

            <p className="mt-2 text-xs text-slate-500">
              {card.description}
            </p>
          </div>
        ))}
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <h2 className="text-lg font-bold text-white">
              Average Fraud Score
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              Average score across recorded transactions
            </p>
          </div>

          <p className="text-4xl font-bold text-indigo-400">
            {stats.average}
            <span className="text-base text-slate-500"> / 100</span>
          </p>
        </div>

        <div className="mt-5 h-3 overflow-hidden rounded-full bg-slate-800">
          <div
            className="h-full rounded-full bg-indigo-500 transition-all"
            style={{ width: `${Math.min(stats.average, 100)}%` }}
          />
        </div>
      </div>

      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h2 className="text-lg font-bold text-white">
            Transaction Risk Analysis
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Review transactions using their backend-generated fraud scores.
          </p>
        </div>

        <div className="flex flex-col gap-4 p-5 lg:flex-row lg:items-center lg:justify-between">
          <div className="flex flex-wrap gap-2">
            {filters.map((filter) => (
              <button
                key={filter}
                onClick={() => setActiveFilter(filter)}
                className={`rounded-lg px-4 py-2 text-xs font-semibold transition ${
                  activeFilter === filter
                    ? 'bg-indigo-600 text-white'
                    : 'border border-slate-700 text-slate-400 hover:bg-slate-800'
                }`}
              >
                {filter}
              </button>
            ))}
          </div>

          <input
            type="search"
            value={search}
            onChange={(event) => setSearch(event.target.value)}
            placeholder="Search payment ID or transaction ID"
            className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-indigo-500 lg:max-w-sm"
          />
        </div>

        {filteredPayments.length === 0 ? (
          <div className="p-10 text-center">
            <h3 className="font-semibold text-white">
              No matching transactions
            </h3>

            <p className="mt-2 text-sm text-slate-400">
              {payments.length === 0
                ? 'Create a payment first to view its fraud analysis.'
                : 'Try changing the risk filter or search term.'}
            </p>

            {payments.length === 0 && (
              <Link
                to="/payments/create"
                className="mt-5 inline-block rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-500"
              >
                Create Payment
              </Link>
            )}
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="bg-slate-950 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-4">Payment ID</th>
                  <th className="px-5 py-4">Transaction ID</th>
                  <th className="px-5 py-4">Amount</th>
                  <th className="px-5 py-4">Fraud Score</th>
                  <th className="px-5 py-4">Risk Level</th>
                  <th className="px-5 py-4">Status</th>
                  <th className="px-5 py-4">Action</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {filteredPayments.map((payment) => {
                  const risk = getRiskLevel(payment)

                  return (
                    <tr
                      key={payment.id}
                      className="text-slate-300 hover:bg-slate-800/40"
                    >
                      <td className="px-5 py-4 font-semibold text-white">
                        #{payment.id}
                      </td>

                      <td className="px-5 py-4">
                        {payment.transaction_id}
                      </td>

                      <td className="px-5 py-4">
                        {payment.currency} {payment.amount}
                      </td>

                      <td className="px-5 py-4 font-semibold">
                        {payment.fraud_score}/100
                      </td>

                      <td className="px-5 py-4">
                        <span
                          className={`rounded-full border px-3 py-1 text-xs font-semibold ${riskStyles[risk]}`}
                        >
                          {risk}
                        </span>
                      </td>

                      <td className="px-5 py-4">
                        {payment.status}
                      </td>

                      <td className="px-5 py-4">
                        <Link
                          to={`/payments/details/${payment.id}`}
                          className="font-semibold text-indigo-400 hover:text-indigo-300"
                        >
                          View Details
                        </Link>
                      </td>
                    </tr>
                  )
                })}
              </tbody>
            </table>
          </div>
        )}
      </div>

      <p className="text-xs leading-6 text-slate-500">
        Fraud analysis is based on backend-generated scores saved with
        successful frontend payment records. This dashboard currently
        displays browser-local history, not all database transactions.
        Educational simulation only.
      </p>
    </div>
  )
}

export default FraudMonitoring
