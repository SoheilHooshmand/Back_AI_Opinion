import { yupResolver } from '@hookform/resolvers/yup'
import { Button, Checkbox, Divider, Paper, PasswordInput, TextInput } from '@mantine/core'
import { useForm } from 'react-hook-form'
import { Link, useNavigate } from '@tanstack/react-router'
import { notifications } from '@mantine/notifications'
import { useState } from 'react'
import styles from './login.module.css'
import { schema } from './utils'
import type { LoginForm } from './utils'
import GoogleBtn from '@/components/GoogleBtn'
import { loginRequest } from '@/api-specs/api'
import setToken from '@/app-util/auth/setToken'

const LoginContainer = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<LoginForm>({
    resolver: yupResolver(schema),
    defaultValues: {
      email: '',
      password: '',
      remember: false,
    },
  })

  const onSubmit = async (values: LoginForm) => {
    setIsLoading(true)
    try {
      const response = await loginRequest(values)
      setToken(response.data.access, response.data.refresh)
      navigate({
        to: '/home',
      })
      setIsLoading(false)
    } catch (error) {
      console.log(error)
      notifications.show({
        title: 'Error',
        message: 'Invalid email or password',
        color: 'red',
      })
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.bg}>
      <Paper radius="lg" p="xl" w={380} bg="accent.1">
        <h1 className={styles.title}>Sign in</h1>
        <p className={styles.subtitle}>Please login to continue to your account.</p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <TextInput
            label="Email"
            placeholder="Enter your email"
            {...register('email')}
            error={errors.email?.message}
            mb="md"
          />

          <PasswordInput
            label="Password"
            placeholder="Enter password"
            {...register('password')}
            error={errors.password?.message}
            mb="md"
          />

          <Checkbox label="Keep me logged in" {...register('remember')} mb="md" />

          <p className={styles.forgot}>Forget my password</p>

          <Button loading={isLoading} fullWidth radius="lg" type="submit" mb="md">
            Sign in
          </Button>

          <Divider label="or" labelPosition="center" my="lg" />

          <GoogleBtn onClick={() => console.log('clicked')} />

          <p className={styles.bottom}>
            Need an account?{' '}
            <Link to="/signup" className={styles.link}>
              Create one
            </Link>
          </p>
        </form>
      </Paper>
    </div>
  )
}

export default LoginContainer
