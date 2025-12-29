import { createFileRoute } from '@tanstack/react-router'
import LoginContainer from '@/containers/login'

export const Route = createFileRoute('/login')({
  component: Login,
})

function Login() {
  return <LoginContainer />
}

export default Login
