import { Outlet, createFileRoute } from '@tanstack/react-router'
import DashboardLayout from '@/layouts/DashboardLayout'

export const Route = createFileRoute('/_authLayout')({
  component: AuthLayout,
})

function AuthLayout() {
  return (
    <div>
      <DashboardLayout>
        <Outlet />
      </DashboardLayout>
    </div>
  )
}
