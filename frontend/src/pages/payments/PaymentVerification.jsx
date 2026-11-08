
import { useState } from 'react'
import { verifyPayment } from '../../services/paymentService'
import { updatePaymentInHistory } from '../../services/paymentHistoryService'

function PaymentVerification() {
  const [paymentId, setPaymentId] = useState('')
  const [gatewayStatus, setGatewayStatus] = useState('SUCCESS')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [payment, setPayment] = useState(null)

  const handleSubmit = async (event) => {
    event.preventDefault()

    setError('')
    setPayment(null)

    if (!Number.isInteger(Number(paymentId)) || Number(paymentId) <= 0) {
      setError('Please enter a valid positive Payment ID.')
      return
    }

    setLoading(true)

    try {
      const response = await verifyPayment(
        paymentId,
        gatewayStatus || null,
      )

      updatePaymentInHistory(response)
      setPayment(response)
    } catch (err) {
      const detail = err.response?.data?.detail

      setError(
        typeof detail === 'string'
          ? detail
          : 'Unable to verify payment. Check the Payment ID and API connection.',
      )
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <p className="text-sm font-medium text-indigo-400">
          PAYMENT MANAGEMENT
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Verify Payment
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Verify a simulated transaction using its Payment ID.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="paymentId"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Payment ID
            </label>

            <input
              id="paymentId"
              type="number"
              min="1"
              step="1"
              required
              value={paymentId}
              onChange={(event) => setPaymentId(event.target.value)}
              placeholder="Enter Payment ID"
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div>
            <label
              htmlFor="gatewayStatus"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Simulated Gateway Result
            </label>

            <select
              id="gatewayStatus"
              value={gatewayStatus}
              onChange={(event) => setGatewayStatus(event.target.value)}
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-indigo-500"
            >
              <option value="SUCCESS">SUCCESS</option>
              <option value="FAILED">FAILED</option>
              <option value="TIMEOUT">TIMEOUT</option>
            </select>

            <p className="mt-2 text-xs text-slate-500">
              Select the simulated gateway response for verification.
            </p>
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
            >
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Verifying Payment...' : 'Verify Payment'}
          </button>
        </form>
      </div>

      {payment && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <h2 className="mb-6 text-xl font-bold text-white">
            Verification Result
          </h2>

          <div className="grid gap-5 sm:grid-cols-2">
            <div>
              <p className="text-xs text-slate-500">Payment ID</p>
              <p className="mt-1 font-semibold text-white">{payment.id}</p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Transaction ID</p>
              <p className="mt-1 break-all font-semibold text-white">
                {payment.transaction_id}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Amount</p>
              <p className="mt-1 font-semibold text-white">
                {payment.currency} {payment.amount}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Payment Method</p>
              <p className="mt-1 font-semibold text-white">
                {payment.payment_method}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Payment Status</p>
              <p className="mt-1 font-semibold text-indigo-300">
                {payment.status}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Fraud Score</p>
              <p className="mt-1 font-semibold text-white">
                {payment.fraud_score}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">Risk Level</p>
              <p className="mt-1 font-semibold text-white">
                {payment.risk_level}
              </p>
            </div>

            <div>
              <p className="text-xs text-slate-500">
                Gateway Transaction ID
              </p>
              <p className="mt-1 break-all font-semibold text-white">
                {payment.gateway_transaction_id || 'Not available'}
              </p>
            </div>
          </div>
        </div>
      )}

      <p className="text-xs leading-6 text-slate-500">
        Educational simulation only. No real bank transactions are processed.
      </p>
    </div>
  )
}

export default PaymentVerification
