
import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { getPayment } from '../../services/paymentService'

function PaymentDetails() {
  const { paymentId } = useParams()
  const [payment, setPayment] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const isValidPaymentId = /^[1-9]\d*$/.test(paymentId || '')
const displayedError = isValidPaymentId
  ? error
  : 'Invalid Payment ID.'

  useEffect(() => {
  let active = true

  async function loadPayment() {
    setLoading(true)
    setError('')

    try {
      const response = await getPayment(paymentId)

      if (active) {
        setPayment(response)
      }
    } catch (err) {
      if (active) {
        const detail = err.response?.data?.detail

        setError(
          typeof detail === 'string'
            ? detail
            : 'Unable to retrieve this transaction. Check the Payment ID and API connection.',
        )
      }
    } finally {
      if (active) {
        setLoading(false)
      }
    }
  }

  if (isValidPaymentId) {
    loadPayment()
  }

  return () => {
    active = false
  }
}, [paymentId, isValidPaymentId])

  const details = payment
    ? [
        ['Payment ID', payment.id],
        ['Transaction ID', payment.transaction_id],
        ['User ID', payment.user_id],
        ['Amount', `${payment.currency} ${payment.amount}`],
        ['Payment Method', payment.payment_method],
        ['Payment Status', payment.status],
        ['Fraud Score', payment.fraud_score],
        ['Risk Level', payment.risk_level],
        [
          'Gateway Transaction ID',
          payment.gateway_transaction_id || 'Not available',
        ],
      ]
    : []

  return (
    <div className="mx-auto max-w-5xl space-y-8">
      <div>
        <p className="text-sm font-medium text-indigo-400">
          PAYMENT MANAGEMENT
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Transaction Details
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Detailed information for payment #{paymentId}.
        </p>
      </div>

      {isValidPaymentId && loading && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-8 text-slate-300">
          Loading transaction details...
        </div>
      )}

      {displayedError && (
        <div
          role="alert"
          className="rounded-2xl border border-red-500/30 bg-red-500/10 p-6 text-red-300"
        >
          {displayedError}
        </div>
      )}

      {payment && isValidPaymentId && (
        <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6 sm:p-8">
          <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
            <div>
              <h2 className="text-xl font-bold text-white">
                Transaction Information
              </h2>
              <p className="mt-1 text-sm text-slate-400">
                Backend payment record
              </p>
            </div>

            <span className="rounded-full bg-indigo-500/10 px-4 py-2 text-sm font-semibold text-indigo-300">
              {payment.status}
            </span>
          </div>

          <div className="grid gap-6 sm:grid-cols-2">
            {details.map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                  {label}
                </p>

                <p className="mt-2 break-all font-semibold text-white">
                  {value}
                </p>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="flex flex-wrap gap-3">
        <Link
          to="/payments/history"
          className="rounded-xl border border-slate-700 px-5 py-3 text-sm font-semibold text-slate-300 hover:bg-slate-800"
        >
          Back to Payment History
        </Link>

        <Link
          to="/payments/create"
          className="rounded-xl bg-indigo-600 px-5 py-3 text-sm font-semibold text-white hover:bg-indigo-500"
        >
          Create Payment
        </Link>
      </div>

      <p className="text-xs leading-6 text-slate-500">
        Transaction details are retrieved from the SmartPay backend.
        Educational simulation only.
      </p>
    </div>
  )
}

export default PaymentDetails
