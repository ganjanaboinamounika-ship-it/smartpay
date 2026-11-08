
const PAYMENT_HISTORY_KEY = 'smartpay_payment_history'

// Get locally saved payment records
export function getPaymentHistory() {
  try {
    const history = localStorage.getItem(PAYMENT_HISTORY_KEY)
    return history ? JSON.parse(history) : []
  } catch (error) {
    console.error('Unable to read payment history:', error)
    return []
  }
}

// Save a newly created payment or update an existing payment
export function savePaymentToHistory(payment) {
  try {
    const history = getPaymentHistory()

    const existingIndex = history.findIndex(
      (item) => String(item.id) === String(payment.id),
    )

    let updatedHistory

    if (existingIndex !== -1) {
      updatedHistory = [...history]
      updatedHistory[existingIndex] = {
        ...updatedHistory[existingIndex],
        ...payment,
      }
    } else {
      updatedHistory = [payment, ...history]
    }

    localStorage.setItem(
      PAYMENT_HISTORY_KEY,
      JSON.stringify(updatedHistory),
    )

    return updatedHistory
  } catch (error) {
    console.error('Unable to save payment history:', error)
    throw error
  }
}

// Update payment details after backend verification
export function updatePaymentInHistory(payment) {
  return savePaymentToHistory(payment)
}
