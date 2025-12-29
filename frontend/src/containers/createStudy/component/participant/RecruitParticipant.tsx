import { Button, NumberInput, Paper, Radio, Select } from '@mantine/core'
import { Controller, useFormContext } from 'react-hook-form'
import { IconPlus } from '@tabler/icons-react'
import styles from './participant.module.css'
import type { ICreateStudyForm } from '@/containers/utils'

export type ScreeningMode = 'new' | 'saved'
export type ParticipantLocation = 'us' | 'ca'

function RecruitParticipantsSection() {
  const {
    control,
    register,
    watch,
    formState: { errors },
  } = useFormContext<ICreateStudyForm>()

  const screeningMode = watch('screeningMode')

  return (
    <Paper radius="lg" p="md" className={styles.card}>
      <h2 className={styles.title}>Recruit silicon participants</h2>

      {/* ---------- Count ---------- */}
      <label className={styles.label}>How many silicon participants are you looking to?</label>
      <Controller
        name="siliconParticipants"
        control={control}
        render={({ field }) => (
          <NumberInput
            {...field}
            placeholder="Text field data"
            error={errors.siliconParticipants?.message}
            value={field.value ?? 0}
            onChange={(value) => field.onChange(value)}
            min={0}
          />
        )}
      />

      {/* ---------- Screening ---------- */}
      <h3 className={styles.subTitle}>Screening</h3>

      <div className={styles.radioGroup}>
        <Radio value={'new'} {...register('screeningMode')} label="Choose new screeners" />

        <Radio value={'saved'} {...register('screeningMode')} label="Use a saved screener set" />
      </div>

      {screeningMode === 'saved' && (
        <div className={styles.selectWrapper}>
          <label className={styles.smallLabel}>Select a screener set</label>
          <Controller
            name="screenerSet"
            control={control}
            render={({ field }) => (
              <Select
                {...field}
                placeholder="Dropdown field data"
                data={[
                  { label: 'General demographics', value: 'general' },
                  { label: 'Tech users', value: 'tech' },
                ]}
                value={field.value ?? null}
                onChange={(value) => field.onChange(value)}
                error={errors.screenerSet?.message}
              />
            )}
          />
        </div>
      )}

      {/* ---------- Location ---------- */}
      <h3 className={styles.subTitle}>Location</h3>
      <p className={styles.helper}>Where should your participants be located?</p>

      <div className={styles.locationGroup}>
        <Radio value={'us'} {...register('location')} />
        <label className={styles.locationOption}>
          <span className={styles.flag}>US</span>
        </label>

        <Radio value={'ca'} {...register('location')} />
        <label className={styles.locationOption}>
          <span className={styles.flag}>🇨🇦</span>
        </label>
      </div>

      <hr className={styles.divider} />

      {/* ---------- Prescreen ---------- */}
      <h3 className={styles.subTitle}>Prescreen participants</h3>
      <p className={styles.helper}>Define the right silicon users for your study using our 300+ screeners.</p>

      <Button bg="accent.6" leftSection={<IconPlus size={16} />}>
        Add screener
      </Button>
    </Paper>
  )
}

export default RecruitParticipantsSection
