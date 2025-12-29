import { Card } from '@mantine/core'
import { Link } from '@tanstack/react-router'
import { useState } from 'react'
import CreateStudyModal from '../priceCalculator/components/CreateStudyModal'
import styles from './home.module.css'

const DashboardHome = () => {
  const [openCreateStudyModal, setOpenCreateStudyModal] = useState(false)
  return (
    <>
      <div className={styles.wrapper}>
        <p className={styles.sectionTitle}>Explore what you can do with Prolific</p>

        <div className={styles.grid}>
          <Link to={'/price-calculator'} className={styles.link}>
            <Card withBorder radius="md" className={styles.card}>
              <div className={styles.imageContainer}>
                <img src={'/imgs/calculator.png'} alt="Pricing calculator" className={styles.image} />
              </div>

              <p className={styles.cardTitle}>Pricing calculator</p>
              <p className={styles.cardDesc}>Estimate the cost of your study before starting research.</p>
            </Card>
          </Link>

          <Card withBorder radius="md" className={styles.card} onClick={() => setOpenCreateStudyModal(true)}>
            <div className={styles.imageContainer}>
              <img src={'/imgs/study.png'} alt="Create study" className={styles.image} />
            </div>
            <p className={styles.cardTitle}>Create study</p>
            <p className={styles.cardDesc}>Complete the form, link your tools, and start your research.</p>
          </Card>

          <Link to={'/'} className={styles.link}>
            <Card withBorder radius="md" className={styles.card}>
              <div className={styles.imageContainer}>
                <img src={'/imgs/updates.png'} alt="Product updates" className={styles.image} />
              </div>
              <p className={styles.cardTitle}>Product updates</p>
              <p className={styles.cardDesc}>Catch up with the latest features and updates.</p>
            </Card>
          </Link>
        </div>
      </div>

      <CreateStudyModal opened={openCreateStudyModal} setOpened={setOpenCreateStudyModal} />
    </>
  )
}

export default DashboardHome
