
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'

import Login from '../pages/auth/Login'
import Register from '../pages/auth/Register'
import Dashboard from '../pages/dashboard/Dashboard'
import CreatePayment from '../pages/payments/CreatePayment'
import PaymentVerification from '../pages/payments/PaymentVerification'
import PaymentHistory from '../pages/payments/PaymentHistory'
import PaymentDetails from '../pages/payments/PaymentDetails'

import DashboardLayout from '../components/layout/DashboardLayout'
import ProtectedRoute from './ProtectedRoute'
import FraudMonitoring from '../pages/fraud/FraudMonitoring'
import WebhookMonitoring from '../pages/webhooks/WebhookMonitoring'

function AppRouter() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Navigate to="/login" replace />} />

        <Route path="/login" element={<Login />} />

        <Route path="/register" element={<Register />} />

        <Route
          path="/dashboard"
          element={
            <ProtectedRoute>
              <Dashboard />
            </ProtectedRoute>
          }
        />

        <Route
          path="/payments/create"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <CreatePayment />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/payments/verify"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <PaymentVerification />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="/payments/history"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <PaymentHistory />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />
        <Route
  path="/fraud"
  element={
    <ProtectedRoute>
      <DashboardLayout>
        <FraudMonitoring />
      </DashboardLayout>
    </ProtectedRoute>
  }
/>

        <Route
  path="/webhooks"
  element={
    <ProtectedRoute>
      <DashboardLayout>
        <WebhookMonitoring />
      </DashboardLayout>
    </ProtectedRoute>
  }
/>
        <Route
          path="/payments/details/:paymentId"
          element={
            <ProtectedRoute>
              <DashboardLayout>
                <PaymentDetails />
              </DashboardLayout>
            </ProtectedRoute>
          }
        />

        <Route
          path="*"
          element={
            <div className="flex min-h-screen items-center justify-center bg-slate-950 text-white">
              <div className="text-center">
                <h1 className="text-5xl font-bold">404</h1>
                <p className="mt-3 text-slate-400">Page not found</p>
              </div>
            </div>
          }
        />
      </Routes>
    </BrowserRouter>
  )
}

export default AppRouter
