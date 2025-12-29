import React from 'react'
import { Button, Divider, Paper } from '@mantine/core'

import styles from './summary.module.css'

const Summary: React.FC = () => {
  return (
    <>
      {/* Participant Cost */}
      <Paper p="lg" radius="md" bg="transparent" withBorder>
        <div className={styles.infoContainer}>
          <p className={styles.infoTitle}>Participant cost</p>
          <div className={styles.boxContainer}>
            <div className={styles.row}>
              <p className={styles.infoText}>No. of silicon users:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>Study time:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>Cost per silicon user:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>GPT Model:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>Number of questions:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>Number of screeners:</p>
              <p className={styles.infoText}>-</p>
            </div>
          </div>
          <Divider my="xs" />
          <div className={styles.row}>
            <p className={styles.totalText}>Total</p>
            <p className={styles.infoText}>-</p>
          </div>
        </div>
      </Paper>

      {/* Fees */}
      <Paper p="lg" radius="md" bg="transparent" withBorder>
        <div className={styles.infoContainer}>
          <p className={styles.infoTitle}>Fees</p>
          <div className={styles.boxContainer}>
            <div className={styles.row}>
              <p className={styles.infoText}>Platform:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <p className={styles.subTitle}>(academic plan)</p>
            <div className={styles.row}>
              <p className={styles.infoText}>VAT:</p>
              <p className={styles.infoText}>-</p>
            </div>
          </div>
          <Divider my="xs" />
          <div className={styles.row}>
            <p className={styles.totalText}>Total</p>
            <p className={styles.infoText}>-</p>
          </div>
        </div>
      </Paper>

      {/* Total */}
      <Paper p="lg" radius="md" bg="transparent" withBorder>
        <div className={styles.infoContainer}>
          <p className={styles.infoTitle}>Total</p>
          <div className={styles.boxContainer}>
            <div className={styles.row}>
              <p className={styles.infoText}>Available balance:</p>
              <p className={styles.infoText}>-</p>
            </div>
            <div className={styles.row}>
              <p className={styles.infoText}>Remaining balance:</p>
              <p className={styles.infoText}>-</p>
            </div>
          </div>
        </div>
      </Paper>

      {/* Action Buttons */}
      <div className={styles.infoContainer}>
        <Button fullWidth size="md">
          Publish now
        </Button>
        <Button fullWidth size="md" variant="outline">
          Save as draft
        </Button>
        <Button fullWidth size="md" variant="outline">
          Schedule publish
        </Button>
      </div>
    </>
  )
}

export default Summary
