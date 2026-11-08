
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { getPaymentHistory } from '../../services/paymentHistoryService'

function PaymentHistory() {
  const [payments] = useState(() => getPaymentHistory())

  const getStatusStyle = (status) => {
    switch (status) {
      case 'SUCCESS':
        return 'bg-emerald-500/10 text-emerald-400'
      case 'FAILED':
        return 'bg-red-500/10 text-red-400'
      case 'PENDING':
        return 'bg-yellow-500/10 text-yellow-400'
      case 'REFUNDED':
        return 'bg-purple-500/10 text-purple-400'
      default:
        return 'bg-slate-700 text-slate-300'
    }
  }

  return (
    <div className="mx-auto max-w-6xl space-y-8">
      <div>
        <p className="text-sm font-medium text-indigo-400">
          PAYMENT MANAGEMENT
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Payment History
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          View payment transactions saved in this browser.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <div className="flex flex-wrap items-center justify-between gap-4">
          <div>
            <p className="text-sm text-slate-400">Saved transactions</p>
            <p className="mt-1 text-3xl font-bold text-white">
              {payments.length}
            </p>
          </div>

          <Link
            to="/payments/create"
            className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500"
          >
            Create Payment
          </Link>
        </div>
      </div>

      {payments.length === 0 ? (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-10 text-center">
          <h2 className="text-xl font-semibold text-white">
            No payment history yet
          </h2>

          <p className="mt-3 text-sm text-slate-400">
            Payments successfully created through this browser will appear here.
          </p>

          <Link
            to="/payments/create"
            className="mt-6 inline-block rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500"
          >
            Create Your First Payment
          </Link>
        </div>
      ) : (
        <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
          <div className="border-b border-slate-800 p-6">
            <h2 className="text-lg font-semibold text-white">
              Transaction Records
            </h2>
          </div>

          <div className="overflow-x-auto">
            <table className="w-full min-w-[750px] text-left text-sm">
              <thead className="bg-slate-950 text-xs uppercase text-slate-400">
                <tr>
                  <th className="px-6 py-4">Payment ID</th>
                  <th className="px-6 py-4">Transaction ID</th>
                  <th className="px-6 py-4">Amount</th>
                  <th className="px-6 py-4">Method</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4">Details</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {payments.map((payment) => (
                  <tr key={payment.id} className="text-slate-300">
                    <td className="px-6 py-4 font-medium text-white">
                      #{payment.id}
                    </td>

                    <td className="max-w-[180px] truncate px-6 py-4">
                      {payment.transaction_id}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4">
                      {payment.currency} {payment.amount}
                    </td>

                    <td className="whitespace-nowrap px-6 py-4">
                      {payment.payment_method}
                    </td>

                    <td className="px-6 py-4">
                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${getStatusStyle(payment.status)}`}
                      >
                        {payment.status}
                      </span>
                    </td>

                    <td className="px-6 py-4">
                      <Link
                        to={`/payments/details/${payment.id}`}
                        className="font-medium text-indigo-400 hover:text-indigo-300"
                      >
                        View Details
                      </Link>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <p className="text-xs leading-6 text-slate-500">
        History is stored locally in this browser. It is not a complete
        server-side payment history.
      </p>
    </div>
  )
}

export default PaymentHistory
