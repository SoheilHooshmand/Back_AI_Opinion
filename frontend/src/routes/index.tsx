import { createFileRoute, useNavigate } from '@tanstack/react-router'
import { Button, Container, Paper } from '@mantine/core'
import { IconUser } from '@tabler/icons-react'
import styles from './landing.module.css'

export const Route = createFileRoute('/')({
  component: App,
})

function App() {
  const navigate = useNavigate()
  const gotoLogin = () => {
    navigate({
      to: '/login',
    })
  }
  return (
    <Container size="lg">
      <div className={styles.wrapper}>
        {/* Header */}
        <div className={styles.header}>
          <Button onClick={gotoLogin} variant="outline" size="sm" leftSection={<IconUser size={16} />}>
            Sign in
          </Button>
        </div>

        {/* Hero */}
        <Paper radius="lg" className={styles.hero}>
          <div className={styles.heroContent}>
            <div className={styles.heroText}>
              <h1 className={styles.title}>
                Quality data.
                <br />
                From powerful AI.
                <br />
                For faster breakthroughs.
              </h1>

              <p className={styles.subtitle}>
                Get set up fast on our self-serve platform and collect complete datasets in less than 2 hours.
              </p>

              <Button size="md" radius="md">
                Start collecting data
              </Button>
            </div>

            <div className={styles.heroImage}>
              <img src="/imgs/hero.gif" alt="AI visual" className={styles.image} />
            </div>
          </div>
        </Paper>
      </div>
    </Container>
  )
}
