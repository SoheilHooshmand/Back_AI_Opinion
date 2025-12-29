import { createFileRoute } from '@tanstack/react-router'
import DashboardHome from '@/containers/home'

export const Route = createFileRoute('/_authLayout/home')({
  component: HomeComponent,
})

function HomeComponent() {
  return <DashboardHome />
}
