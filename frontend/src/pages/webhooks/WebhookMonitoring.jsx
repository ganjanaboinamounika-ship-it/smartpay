
import { useCallback, useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import {
  getWebhooks,
  registerWebhook,
  deactivateWebhook,
  getWebhookDeliveries,
  getWebhookDelivery,
  retryWebhookDelivery,
} from '../../services/webhookService'

const deliveryStatuses = [
  'ALL',
  'PENDING',
  'PROCESSING',
  'DELIVERED',
  'FAILED',
]

function WebhookMonitoring() {
  const [endpoints, setEndpoints] = useState([])
  const [deliveries, setDeliveries] = useState([])
  const [totalDeliveries, setTotalDeliveries] = useState(0)

  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [success, setSuccess] = useState('')

  const [url, setUrl] = useState('')
  const [events, setEvents] = useState(['payment.success'])
  const [registering, setRegistering] = useState(false)

  const [activeFilter, setActiveFilter] = useState('ALL')
  const [selectedDelivery, setSelectedDelivery] = useState(null)
  const [secret, setSecret] = useState('')
  const [actionId, setActionId] = useState(null)

  // Add or remove subscribed webhook events.
  const handleEventChange = (eventName, checked) => {
    setEvents((currentEvents) => {
      if (checked) {
        return currentEvents.includes(eventName)
          ? currentEvents
          : [...currentEvents, eventName]
      }

      return currentEvents.filter(
        (currentEvent) => currentEvent !== eventName,
      )
    })
  }

  // Convert API errors into readable messages.
  const getErrorMessage = useCallback((err) => {
    const detail = err.response?.data?.detail

    if (typeof detail === 'string') {
      return detail
    }

    if (Array.isArray(detail)) {
      return detail.map((item) => item.msg).join(', ')
    }

    return 'Something went wrong. Please check the API connection and try again.'
  }, [])

  // Retrieve webhook endpoints and delivery records.
  const fetchDashboard = useCallback(async (status = 'ALL') => {
    const [endpointData, deliveryData] = await Promise.all([
      getWebhooks(),
      getWebhookDeliveries({
        status: status === 'ALL' ? undefined : status,
        limit: 100,
        offset: 0,
      }),
    ])

    return {
      endpoints: Array.isArray(endpointData) ? endpointData : [],
      deliveries: deliveryData.items || [],
      total: deliveryData.total || 0,
    }
  }, [])

  // Refresh dashboard data after user actions.
  const loadDashboard = useCallback(
    async (status = 'ALL') => {
      setLoading(true)
      setError('')

      try {
        const data = await fetchDashboard(status)

        setEndpoints(data.endpoints)
        setDeliveries(data.deliveries)
        setTotalDeliveries(data.total)
      } catch (err) {
        setError(getErrorMessage(err))
      } finally {
        setLoading(false)
      }
    },
    [fetchDashboard, getErrorMessage],
  )

  // Load data initially and whenever the delivery filter changes.
  useEffect(() => {
    let active = true

    async function loadInitialDashboard() {
      try {
        const data = await fetchDashboard(activeFilter)

        if (active) {
          setEndpoints(data.endpoints)
          setDeliveries(data.deliveries)
          setTotalDeliveries(data.total)
          setError('')
        }
      } catch (err) {
        if (active) {
          setError(getErrorMessage(err))
        }
      } finally {
        if (active) {
          setLoading(false)
        }
      }
    }

    loadInitialDashboard()

    return () => {
      active = false
    }
  }, [fetchDashboard, activeFilter, getErrorMessage])

  // Register a new webhook endpoint.
  const handleRegister = async (event) => {
    event.preventDefault()
    setError('')
    setSuccess('')
    setSecret('')

    if (!url.trim()) {
      setError('Please enter a webhook URL.')
      return
    }

    if (events.length === 0) {
      setError('Select at least one webhook event.')
      return
    }

    setRegistering(true)

    try {
      const response = await registerWebhook({
        url: url.trim(),
        events,
      })

      setSecret(response.secret || '')
      setSuccess(
        `Webhook endpoint #${response.id} registered successfully.`,
      )
      setUrl('')
      setEvents(['payment.success'])

      await loadDashboard(activeFilter)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setRegistering(false)
    }
  }

  // Deactivate an existing webhook endpoint.
  const handleDeactivate = async (endpointId) => {
    const confirmed = window.confirm(
      `Are you sure you want to deactivate webhook endpoint #${endpointId}?`,
    )

    if (!confirmed) return

    setError('')
    setSuccess('')
    setActionId(endpointId)

    try {
      await deactivateWebhook(endpointId)

      setSuccess(`Webhook endpoint #${endpointId} deactivated.`)
      await loadDashboard(activeFilter)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionId(null)
    }
  }

  // Retry a failed webhook delivery.
  const handleRetry = async (deliveryId) => {
    setError('')
    setSuccess('')
    setActionId(deliveryId)

    try {
      await retryWebhookDelivery(deliveryId)

      setSuccess(
        `Retry request for delivery #${deliveryId} was accepted by the API.`,
      )

      await loadDashboard(activeFilter)
    } catch (err) {
      setError(getErrorMessage(err))
    } finally {
      setActionId(null)
    }
  }

  // Retrieve complete delivery details.
  const handleViewDetails = async (deliveryId) => {
    setError('')
    setSelectedDelivery(null)

    try {
      const response = await getWebhookDelivery(deliveryId)
      setSelectedDelivery(response)
    } catch (err) {
      setError(getErrorMessage(err))
    }
  }

  // Copy the generated webhook secret.
  const copySecret = async () => {
    try {
      await navigator.clipboard.writeText(secret)
      setSuccess('Webhook secret copied. Store it securely.')
    } catch {
      setError(
        'Unable to copy automatically. Select and copy the secret manually.',
      )
    }
  }

  // Dashboard statistics.
  const stats = {
    endpoints: endpoints.length,
    active: endpoints.filter((item) => item.is_active).length,
    delivered: deliveries.filter(
      (item) => item.status === 'DELIVERED',
    ).length,
    failed: deliveries.filter(
      (item) => item.status === 'FAILED',
    ).length,
    pending: deliveries.filter(
      (item) => ['PENDING', 'PROCESSING'].includes(item.status),
    ).length,
  }

  const statusStyles = {
    PENDING: 'bg-amber-500/10 text-amber-400 border-amber-500/20',
    PROCESSING: 'bg-indigo-500/10 text-indigo-400 border-indigo-500/20',
    DELIVERED: 'bg-emerald-500/10 text-emerald-400 border-emerald-500/20',
    FAILED: 'bg-red-500/10 text-red-400 border-red-500/20',
  }

  const statCards = [
    {
      label: 'Total Endpoints',
      value: stats.endpoints,
      color: 'text-white',
    },
    {
      label: 'Active Endpoints',
      value: stats.active,
      color: 'text-emerald-400',
    },
    {
      label: 'Delivered',
      value: stats.delivered,
      color: 'text-emerald-400',
    },
    {
      label: 'Failed Deliveries',
      value: stats.failed,
      color: 'text-red-400',
    },
  ]

  return (
    <div className="mx-auto max-w-7xl space-y-8">
      {/* Page heading */}
      <div>
        <p className="text-sm font-medium text-indigo-400">
          EVENT DELIVERY MANAGEMENT
        </p>

        <h1 className="mt-2 text-3xl font-bold text-white">
          Webhook Monitoring
        </h1>

        <p className="mt-2 text-sm text-slate-400">
          Manage webhook endpoints and monitor payment event deliveries.
        </p>
      </div>

      {/* Error message */}
      {error && (
        <div
          role="alert"
          className="rounded-xl border border-red-500/30 bg-red-500/10 p-4 text-sm text-red-300"
        >
          {error}
        </div>
      )}

      {/* Success message */}
      {success && (
        <div
          role="status"
          className="rounded-xl border border-emerald-500/30 bg-emerald-500/10 p-4 text-sm text-emerald-300"
        >
          {success}
        </div>
      )}

      {/* Newly generated webhook secret */}
      {secret && (
        <div className="rounded-2xl border border-amber-500/30 bg-amber-500/10 p-6">
          <h2 className="font-bold text-amber-300">
            Save Your Webhook Secret
          </h2>

          <p className="mt-2 text-sm text-slate-300">
            This secret was returned during registration. Store it securely.
            Do not share it publicly.
          </p>

          <div className="mt-4 flex flex-col gap-3 sm:flex-row">
            <input
              type="text"
              readOnly
              value={secret}
              className="min-w-0 flex-1 rounded-lg border border-slate-700 bg-slate-950 p-3 text-sm text-white"
            />

            <button
              type="button"
              onClick={copySecret}
              className="rounded-lg bg-amber-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-amber-400"
            >
              Copy Secret
            </button>
          </div>

          <button
            type="button"
            onClick={() => setSecret('')}
            className="mt-3 text-xs text-slate-400 underline"
          >
            Hide Secret
          </button>
        </div>
      )}

      {/* Statistics */}
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
          </div>
        ))}
      </div>

      {/* Register webhook endpoint */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900 p-6">
        <h2 className="text-lg font-bold text-white">
          Register Webhook Endpoint
        </h2>

        <p className="mt-1 text-sm text-slate-400">
          Subscribe an endpoint to SmartPay payment events.
        </p>

        <form onSubmit={handleRegister} className="mt-6 space-y-5">
          <div>
            <label className="mb-2 block text-sm font-medium text-slate-300">
              Endpoint URL
            </label>

            <input
              type="url"
              required
              maxLength={2048}
              value={url}
              onChange={(event) => setUrl(event.target.value)}
              placeholder="https://example.com/webhooks/smartpay"
              className="w-full rounded-xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-indigo-500"
            />
          </div>

          <div>
            <p className="mb-3 text-sm font-medium text-slate-300">
              Subscribe to Events
            </p>

            <div className="flex flex-wrap gap-4">
              {['payment.success', 'payment.failed'].map((eventName) => (
                <label
                  key={eventName}
                  className="flex items-center gap-2 text-sm text-slate-300"
                >
                  <input
                    type="checkbox"
                    checked={events.includes(eventName)}
                    onChange={(event) =>
                      handleEventChange(eventName, event.target.checked)
                    }
                    className="h-4 w-4 accent-indigo-500"
                  />

                  {eventName}
                </label>
              ))}
            </div>
          </div>

          <button
            type="submit"
            disabled={registering}
            className="rounded-xl bg-indigo-600 px-6 py-3 text-sm font-semibold text-white transition hover:bg-indigo-500 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {registering ? 'Registering...' : 'Register Endpoint'}
          </button>
        </form>
      </div>

      {/* Registered webhook endpoints */}
      <div className="rounded-2xl border border-slate-800 bg-slate-900">
        <div className="border-b border-slate-800 p-6">
          <h2 className="text-lg font-bold text-white">
            Registered Webhook Endpoints
          </h2>

          <p className="mt-1 text-sm text-slate-400">
            Manage your registered destination URLs.
          </p>
        </div>

        {loading ? (
          <p className="p-8 text-sm text-slate-400">
            Loading webhook endpoints...
          </p>
        ) : endpoints.length === 0 ? (
          <p className="p-8 text-center text-sm text-slate-400">
            No webhook endpoints registered yet.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[700px] text-left text-sm">
              <thead className="bg-slate-950 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-4">ID</th>
                  <th className="px-5 py-4">Endpoint URL</th>
                  <th className="px-5 py-4">Events</th>
                  <th className="px-5 py-4">Status</th>
                  <th className="px-5 py-4">Action</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {endpoints.map((endpoint) => (
                  <tr key={endpoint.id} className="text-slate-300">
                    <td className="px-5 py-4">#{endpoint.id}</td>

                    <td className="max-w-xs break-all px-5 py-4">
                      {endpoint.url}
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex flex-wrap gap-1">
                        {endpoint.events.map((eventName) => (
                          <span
                            key={eventName}
                            className="rounded-md bg-indigo-500/10 px-2 py-1 text-xs text-indigo-300"
                          >
                            {eventName}
                          </span>
                        ))}
                      </div>
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={
                          endpoint.is_active
                            ? 'text-emerald-400'
                            : 'text-slate-500'
                        }
                      >
                        {endpoint.is_active ? 'ACTIVE' : 'INACTIVE'}
                      </span>
                    </td>

                    <td className="px-5 py-4">
                      {endpoint.is_active && (
                        <button
                          type="button"
                          onClick={() => handleDeactivate(endpoint.id)}
                          disabled={actionId === endpoint.id}
                          className="text-xs font-semibold text-red-400 hover:text-red-300 disabled:opacity-50"
                        >
                          {actionId === endpoint.id
                            ? 'Processing...'
                            : 'Deactivate'}
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Webhook delivery history */}
      <div className="overflow-hidden rounded-2xl border border-slate-800 bg-slate-900">
        <div className="flex flex-wrap items-center justify-between gap-4 border-b border-slate-800 p-6">
          <div>
            <h2 className="text-lg font-bold text-white">
              Webhook Delivery History
            </h2>

            <p className="mt-1 text-sm text-slate-400">
              {totalDeliveries} matching delivery records in the backend.
            </p>
          </div>

          <button
            type="button"
            onClick={() => loadDashboard(activeFilter)}
            disabled={loading}
            className="rounded-lg border border-slate-700 px-4 py-2 text-sm text-slate-300 hover:bg-slate-800 disabled:opacity-50"
          >
            Refresh
          </button>
        </div>

        {/* Delivery status filters */}
        <div className="flex flex-wrap gap-2 p-5">
          {deliveryStatuses.map((status) => (
            <button
              type="button"
              key={status}
              onClick={() => {
                if (status !== activeFilter) {
                  setLoading(true)
                  setActiveFilter(status)
                }
              }}
              className={`rounded-lg px-4 py-2 text-xs font-semibold ${
                activeFilter === status
                  ? 'bg-indigo-600 text-white'
                  : 'border border-slate-700 text-slate-400 hover:bg-slate-800'
              }`}
            >
              {status}
            </button>
          ))}
        </div>

        {loading ? (
          <p className="p-8 text-sm text-slate-400">
            Loading delivery history...
          </p>
        ) : deliveries.length === 0 ? (
          <p className="p-8 text-center text-sm text-slate-400">
            No webhook deliveries found for this filter.
          </p>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full min-w-[850px] text-left text-sm">
              <thead className="bg-slate-950 text-xs uppercase text-slate-500">
                <tr>
                  <th className="px-5 py-4">Delivery ID</th>
                  <th className="px-5 py-4">Payment ID</th>
                  <th className="px-5 py-4">Event Type</th>
                  <th className="px-5 py-4">Attempts</th>
                  <th className="px-5 py-4">HTTP Code</th>
                  <th className="px-5 py-4">Status</th>
                  <th className="px-5 py-4">Action</th>
                </tr>
              </thead>

              <tbody className="divide-y divide-slate-800">
                {deliveries.map((delivery) => (
                  <tr key={delivery.id} className="text-slate-300">
                    <td className="px-5 py-4">#{delivery.id}</td>
                    <td className="px-5 py-4">#{delivery.payment_id}</td>
                    <td className="px-5 py-4">{delivery.event_type}</td>

                    <td className="px-5 py-4">
                      {delivery.attempts}/{delivery.max_attempts}
                    </td>

                    <td className="px-5 py-4">
                      {delivery.http_status_code ?? '—'}
                    </td>

                    <td className="px-5 py-4">
                      <span
                        className={`rounded-full border px-3 py-1 text-xs font-semibold ${
                          statusStyles[delivery.status] ||
                          'border-slate-700 text-slate-400'
                        }`}
                      >
                        {delivery.status}
                      </span>
                    </td>

                    <td className="px-5 py-4">
                      <div className="flex gap-3">
                        <button
                          type="button"
                          onClick={() => handleViewDetails(delivery.id)}
                          className="text-xs font-semibold text-indigo-400 hover:text-indigo-300"
                        >
                          Details
                        </button>

                        {delivery.status === 'FAILED' && (
                          <button
                            type="button"
                            onClick={() => handleRetry(delivery.id)}
                            disabled={actionId === delivery.id}
                            className="text-xs font-semibold text-amber-400 hover:text-amber-300 disabled:opacity-50"
                          >
                            {actionId === delivery.id
                              ? 'Retrying...'
                              : 'Retry'}
                          </button>
                        )}
                      </div>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Selected delivery details */}
      {selectedDelivery && (
        <div className="rounded-2xl border border-indigo-500/30 bg-slate-900 p-6">
          <div className="flex flex-wrap items-center justify-between gap-3">
            <h2 className="text-lg font-bold text-white">
              Delivery #{selectedDelivery.id} Details
            </h2>

            <button
              type="button"
              onClick={() => setSelectedDelivery(null)}
              className="text-sm text-slate-400 hover:text-white"
            >
              Close
            </button>
          </div>

          <div className="mt-5 grid gap-4 sm:grid-cols-2">
            {[
              ['Event ID', selectedDelivery.event_id],
              ['Endpoint ID', selectedDelivery.endpoint_id],
              ['Payment ID', selectedDelivery.payment_id],
              ['Event Type', selectedDelivery.event_type],
              ['Status', selectedDelivery.status],
              [
                'Attempts',
                `${selectedDelivery.attempts}/${selectedDelivery.max_attempts}`,
              ],
              [
                'HTTP Status',
                selectedDelivery.http_status_code ?? 'Not available',
              ],
              ['Created At', selectedDelivery.created_at],
              [
                'Delivered At',
                selectedDelivery.delivered_at || 'Not delivered',
              ],
              [
                'Next Retry',
                selectedDelivery.next_retry_at || 'Not scheduled',
              ],
              ['Last Error', selectedDelivery.last_error || 'None'],
            ].map(([label, value]) => (
              <div
                key={label}
                className="rounded-xl border border-slate-800 bg-slate-950 p-4"
              >
                <p className="text-xs uppercase text-slate-500">{label}</p>

                <p className="mt-2 break-all text-sm text-white">
                  {value}
                </p>
              </div>
            ))}
          </div>

          <div className="mt-5">
            <h3 className="mb-2 text-sm font-semibold text-white">
              Response Body
            </h3>

            <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-xl bg-slate-950 p-4 text-xs text-slate-300">
              {selectedDelivery.response_body ||
                'No response body available.'}
            </pre>
          </div>

          <div className="mt-5">
            <h3 className="mb-2 text-sm font-semibold text-white">
              Event Payload
            </h3>

            <pre className="overflow-x-auto whitespace-pre-wrap break-all rounded-xl bg-slate-950 p-4 text-xs text-slate-300">
              {JSON.stringify(selectedDelivery.payload, null, 2)}
            </pre>
          </div>

          {selectedDelivery.status === 'FAILED' && (
            <button
              type="button"
              onClick={() => handleRetry(selectedDelivery.id)}
              disabled={actionId === selectedDelivery.id}
              className="mt-5 rounded-xl bg-amber-500 px-5 py-3 text-sm font-semibold text-slate-950 hover:bg-amber-400 disabled:opacity-50"
            >
              {actionId === selectedDelivery.id
                ? 'Retrying...'
                : 'Retry This Delivery'}
            </button>
          )}
        </div>
      )}

      {/* Navigation */}
      <div className="flex flex-wrap gap-3">
        <Link
          to="/dashboard"
          className="rounded-xl border border-slate-700 px-5 py-3 text-sm text-slate-300 hover:bg-slate-800"
        >
          Back to Dashboard
        </Link>
      </div>

      <p className="text-xs leading-6 text-slate-500">
        Delivery information is retrieved from the SmartPay backend.
        Delivery statistics reflect the currently loaded delivery results.
        Webhook secrets should be stored securely. Educational simulation only.
      </p>
    </div>
  )
}

export default WebhookMonitoring
