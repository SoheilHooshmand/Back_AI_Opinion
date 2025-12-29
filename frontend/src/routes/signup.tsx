import { createFileRoute } from '@tanstack/react-router'
import SignupContainer from '@/containers/signup'

export const Route = createFileRoute('/signup')({
  component: RouteComponent,
})

function RouteComponent() {
  return <SignupContainer />
}
