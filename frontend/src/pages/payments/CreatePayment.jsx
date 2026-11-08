
import { useState } from 'react'
import { createPayment } from '../../services/paymentService'
import { savePaymentToHistory } from '../../services/paymentHistoryService'

function CreatePayment() {
  const [amount, setAmount] = useState('')
  const [currency, setCurrency] = useState('INR')
  const [paymentMethod, setPaymentMethod] = useState('UPI')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')
  const [payment, setPayment] = useState(null)
  const [idempotencyKey, setIdempotencyKey] = useState('')

  const handleSubmit = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setPayment(null)

    const numericAmount = Number(amount)

    if (!Number.isFinite(numericAmount) || numericAmount <= 0) {
      setError('Please enter a valid amount greater than zero.')
      return
    }

    const normalizedCurrency = currency.trim().toUpperCase()

    if (!/^[A-Z]{3}$/.test(normalizedCurrency)) {
      setError('Currency must be a 3-letter code, such as INR.')
      return
    }

    if (!idempotencyKey && !crypto.randomUUID) {
      setError('Your browser does not support secure request IDs.')
      return
    }

    const requestKey = idempotencyKey || crypto.randomUUID()
    setIdempotencyKey(requestKey)

    setLoading(true)

    try {
      const response = await createPayment(
        {
          amount: numericAmount,
          currency: normalizedCurrency,
          payment_method: paymentMethod,
        },
        requestKey,
      )

      setPayment(response)

// Save the successful payment in browser history
try {
  savePaymentToHistory(response)
  setSuccess('Payment created successfully and saved to payment history.')
} catch (historyError) {
  console.error('Payment history storage failed:', historyError)
  setSuccess('Payment created successfully, but could not be saved to local history.')
}

setIdempotencyKey('')
    } catch (err) {
      setError(
        err.response?.data?.detail ||
          'Unable to create payment. Please check the API connection and try again.',
      )
    } finally {
      setLoading(false)
    }
  }

  const handleFieldChange = (setter) => (event) => {
    setter(event.target.value)
    setIdempotencyKey('')
  }

  return (
    <div className="mx-auto max-w-4xl space-y-8">
      <div>
        <p className="text-sm font-medium text-indigo-400">
          PAYMENT MANAGEMENT
        </p>
        <h1 className="mt-2 text-3xl font-bold text-white">
          Create Payment
        </h1>
        <p className="mt-2 text-sm text-slate-400">
          Submit a payment request through the SmartPay simulation API.
        </p>
      </div>

      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
        <form onSubmit={handleSubmit} className="space-y-6">
          <div>
            <label
              htmlFor="amount"
              className="mb-2 block text-sm font-medium text-slate-300"
            >
              Payment Amount
            </label>
            <input
              id="amount"
              type="number"
              min="0.01"
              step="0.01"
              required
              value={amount}
              onChange={handleFieldChange(setAmount)}
              placeholder="Enter amount"
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-500/20"
            />
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            <div>
              <label
                htmlFor="currency"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Currency
              </label>
              <input
                id="currency"
                type="text"
                maxLength={3}
                required
                value={currency}
                onChange={handleFieldChange(setCurrency)}
                placeholder="INR"
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-indigo-500"
              />
            </div>

            <div>
              <label
                htmlFor="paymentMethod"
                className="mb-2 block text-sm font-medium text-slate-300"
              >
                Payment Method
              </label>
              <select
                id="paymentMethod"
                value={paymentMethod}
                onChange={handleFieldChange(setPaymentMethod)}
                className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-white outline-none transition focus:border-indigo-500"
              >
                <option value="CARD">Card</option>
                <option value="UPI">UPI</option>
                <option value="NET_BANKING">Net Banking</option>
                <option value="WALLET">Wallet</option>
              </select>
            </div>
          </div>

          {error && (
            <div
              role="alert"
              className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
            >
              {error}
            </div>
          )}

          {success && (
            <div
              role="status"
              className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300"
            >
              {success}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-indigo-600 px-5 py-3 font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {loading ? 'Creating Payment...' : 'Create Payment'}
          </button>
        </form>
      </div>

      {payment && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <h2 className="mb-6 text-xl font-bold text-white">
            Payment Response
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
              <p className="text-xs text-slate-500">Status</p>
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
              <p className="text-xs text-slate-500">Gateway Transaction ID</p>
              <p className="mt-1 break-all font-semibold text-white">
                {payment.gateway_transaction_id || 'Not available'}
              </p>
            </div>
          </div>
        </div>
      )}

      <p className="text-xs leading-6 text-slate-500">
        Educational simulation only. This screen does not process real bank
        transactions or collect card details.
      </p>
    </div>
  )
}

export default CreatePayment
