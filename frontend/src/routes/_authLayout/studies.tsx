import { createFileRoute } from '@tanstack/react-router'
import StudiesPage from '@/containers/studies'

export const Route = createFileRoute('/_authLayout/studies')({
  component: RouteComponent,
})

function RouteComponent() {
  return (
    <div>
      <StudiesPage />
    </div>
  )
}
