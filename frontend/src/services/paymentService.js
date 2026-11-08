
import api from './api'

// Create a new payment
export async function createPayment(paymentData, idempotencyKey) {
  const response = await api.post(
    '/payments/create',
    paymentData,
    {
      headers: {
        'Idempotency-Key': idempotencyKey,
      },
    },
  )

  return response.data
}

// Verify an existing payment
export async function verifyPayment(paymentId, gatewayStatus = null) {
  const response = await api.post('/payments/verify', {
    payment_id: Number(paymentId),
    gateway_status: gatewayStatus,
  })

  return response.data
}

// Retrieve payment details
export async function getPayment(paymentId) {
  const response = await api.get(`/payments/${paymentId}`)
  return response.data
}
