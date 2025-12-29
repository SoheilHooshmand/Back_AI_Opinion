import React, { useState } from 'react'
import { Button, Paper, Select } from '@mantine/core'
import { IconClock, IconInfoCircle } from '@tabler/icons-react'
import styles from './cost.module.css'

const CostCalculator: React.FC = () => {
  const [aiModel, setAiModel] = useState<string | null>('scrollor')
  const [calculatedTime, setCalculatedTime] = useState<string>('-')

  const handleCalculate = () => {
    // Simulate calculation
    const randomTime = Math.floor(Math.random() * 30) + 10
    setCalculatedTime(`${randomTime} minutes`)
  }

  return (
    <>
      <div className={styles.wrapper}>
        <p className={styles.title}>Cost</p>

        <Paper p="xl" radius="md" bg="gray.0" withBorder>
          <div className={styles.paperContainer}>
            {/* AI Model Selection */}
            <div className={styles.modelBox}>
              <div>
                <div className={styles.info}>
                  <IconInfoCircle size={16} color="gray" />
                  <p className={styles.infoTitle}>The AI model used</p>
                </div>
                <p className={styles.desc}>The artificial intelligence model used in your project</p>
              </div>

              <Select
                value={aiModel}
                onChange={setAiModel}
                data={[
                  { value: 'scrollor', label: 'Scrollor title' },
                  { value: 'gpt-4', label: 'GPT-4' },
                  { value: 'claude', label: 'Claude' },
                  { value: 'gemini', label: 'Gemini' },
                ]}
                allowDeselect={false}
              />
            </div>

            {/* Recruitment Time Calculator */}
            <Paper p="lg" radius="md" bg="white" withBorder>
              <div>
                <div className={styles.calculateTimeHeader}>
                  <div className={styles.info}>
                    <IconClock size={24} />
                    <p>Calculate your recruitment time</p>
                  </div>
                  <Button onClick={handleCalculate} size="sm">
                    Calculate
                  </Button>
                </div>

                <p className={styles.desc}>
                  Recruitment time is the duration needed to enlist the specified number of silicon users for a study
                  from your requested audience.
                </p>

                <div className={styles.calculateTimeResult}>
                  <p>Time</p>
                  <p>{calculatedTime}</p>
                </div>
              </div>
            </Paper>
          </div>
        </Paper>
      </div>
    </>
  )
}

export default CostCalculator
