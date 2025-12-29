import { yupResolver } from '@hookform/resolvers/yup'
import { Button, Divider, Paper, PasswordInput, TextInput } from '@mantine/core'
import { Link, useNavigate } from '@tanstack/react-router'
import { useForm } from 'react-hook-form'
import { notifications } from '@mantine/notifications'
import { useState } from 'react'
import styles from '../login/login.module.css'
import { schema } from './utils'
import type { SignupForm } from './utils'
import GoogleBtn from '@/components/GoogleBtn'
import { registrationRequest } from '@/api-specs/api'

const SignupContainer = () => {
  const navigate = useNavigate()
  const [isLoading, setIsLoading] = useState(false)
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<SignupForm>({
    resolver: yupResolver(schema),
    defaultValues: {
      email: '',
      password1: '',
      password2: '',
      username: '',
    },
  })

  const onSubmit = async (values: SignupForm) => {
    setIsLoading(true)
    try {
      const response = await registrationRequest(values)
      console.log(response)
      setIsLoading(false)
      navigate({
        to: '/login',
      })
    } catch (error) {
      console.log(error)
      notifications.show({
        title: 'Error',
        message: 'sth wrong happened',
        color: 'red',
      })
      setIsLoading(false)
    }
  }

  return (
    <div className={styles.bg}>
      <Paper radius="lg" p="xl" w={380} bg="accent.1">
        <h1 className={styles.title}>Sign up</h1>
        <p className={styles.subtitle}>Sign up to enjoy the feature of Revolutie</p>

        <form onSubmit={handleSubmit(onSubmit)}>
          <TextInput
            label="Your Name"
            placeholder="Enter your name"
            {...register('username')}
            error={errors.username?.message}
            mb="md"
          />

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
            {...register('password1')}
            error={errors.password1?.message}
            mb="md"
          />

          <PasswordInput
            label="re enter Password"
            placeholder="re enter password"
            {...register('password2')}
            error={errors.password2?.message}
            mb="md"
          />

          <Button loading={isLoading} fullWidth radius="lg" type="submit" mb="md">
            Sign Up
          </Button>

          <Divider label="or" labelPosition="center" my="lg" />

          <GoogleBtn onClick={() => console.log('clicked')} />

          <p className={styles.bottom}>
            Already have an account?{' '}
            <Link to="/login" className={styles.link}>
              Sign in
            </Link>
          </p>
        </form>
      </Paper>
    </div>
  )
}

export default SignupContainer
