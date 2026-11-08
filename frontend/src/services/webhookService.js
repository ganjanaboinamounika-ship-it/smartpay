
import api from './api'

// Retrieve registered webhook endpoints
export async function getWebhooks() {
  const response = await api.get('/webhooks')
  return response.data
}

// Register a new webhook endpoint
export async function registerWebhook(webhookData) {
  const response = await api.post('/webhooks', webhookData)
  return response.data
}

// Deactivate a registered webhook endpoint
export async function deactivateWebhook(endpointId) {
  const response = await api.post(
    `/webhooks/${endpointId}/deactivate`,
  )
  return response.data
}

// Retrieve webhook delivery history
export async function getWebhookDeliveries({
  status,
  limit = 20,
  offset = 0,
} = {}) {
  const response = await api.get('/webhooks/deliveries', {
    params: {
      ...(status ? { status } : {}),
      limit,
      offset,
    },
  })

  return response.data
}

// Retrieve individual delivery details
export async function getWebhookDelivery(deliveryId) {
  const response = await api.get(
    `/webhooks/deliveries/${deliveryId}`,
  )

  return response.data
}

// Retry a failed webhook delivery
export async function retryWebhookDelivery(deliveryId) {
  const response = await api.post(
    `/webhooks/deliveries/${deliveryId}/retry`,
  )

  return response.data
}
