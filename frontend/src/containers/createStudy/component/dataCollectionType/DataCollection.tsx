import { Paper, Radio, TextInput } from '@mantine/core'
import {
  IconChecklist,
  IconFile,
  IconGitBranch,
  IconLink,
  IconList,
  IconPencil,
  IconUsers,
  IconX,
} from '@tabler/icons-react'
import { Controller, useFormContext } from 'react-hook-form'
import styles from './dataCollection.module.css'
import type { ICreateStudyForm, StudyCollectionType } from '@/containers/utils'

export type DataCollectionType =
  | 'external'
  | 'file'
  | 'survey'
  | 'decision'
  | 'writing'
  | 'interview'
  | 'ai-task'
  | 'none'

function DataCollectionSection() {
  const {
    control,
    register,
    formState: { errors },
  } = useFormContext<ICreateStudyForm>()
  return (
    <>
      {/* ---------- Data collection type ---------- */}
      <h2 className={styles.sectionTitle}>Data collection type</h2>
      <Controller
        control={control}
        name="collectionType"
        render={({ field }) => (
          <Paper radius="lg" p="md" className={styles.card}>
            <p className={styles.question}>How do you want to collect your data?</p>

            <div className={styles.optionGrid}>
              <label className={styles.option}>
                <Radio checked={field.value === 'link'} onChange={() => field.onChange('link')} />
                <IconLink size={18} />
                <div>
                  <p className={styles.optionTitle}>External study link</p>
                  <p className={styles.optionDesc}>Provide your own URL</p>
                </div>
              </label>

              <label className={styles.option}>
                <Radio checked={field.value === 'file'} onChange={() => field.onChange('file')} />
                <IconFile size={18} />
                <div>
                  <p className={styles.optionTitle}>As a file</p>
                  <p className={styles.optionDesc}>Provide your own file</p>
                </div>
              </label>
            </div>
          </Paper>
        )}
      />

      {/* ---------- Study details ---------- */}
      <h2 className={styles.sectionTitle}>Study details</h2>

      <Paper radius="lg" p="md" className={styles.card}>
        <label className={styles.label}>Study name</label>
        <TextInput placeholder="Text field data" {...register('studyName')} error={errors.studyName?.message} />

        <label className={styles.label}>Internal study name (optional)</label>
        <TextInput
          placeholder="Text field data"
          {...register('internalStudyName')}
          error={errors.internalStudyName?.message}
        />

        <label className={styles.label}>Study description</label>
        <p className={styles.helper}>Describe what participants will be doing in this study.</p>
        <TextInput placeholder="Text field data" {...register('description')} error={errors.description?.message} />

        <hr className={styles.divider} />

        <p className={styles.question}>How do you want to collect your data?</p>

        <div className={styles.methodGrid}>
          <MethodCard value={'survey'} icon={<IconList />} label="Survey" />
          <MethodCard disabled value={'decision_making'} icon={<IconGitBranch />} label="Decision making" />
          <MethodCard disabled value={'writing'} icon={<IconPencil />} label="Writing" />
          <MethodCard disabled value={'interview'} icon={<IconUsers />} label="Interview" />
          <MethodCard disabled value={'ai-task'} icon={<IconChecklist />} label="AI task" />
          <MethodCard value={'none'} icon={<IconX />} label="None" />
        </div>
      </Paper>
    </>
  )
}

interface MethodCardProps {
  icon: React.ReactNode
  label: string
  value: string
  disabled?: boolean
}

function MethodCard({ icon, label, value, disabled }: MethodCardProps) {
  const { watch, setValue } = useFormContext<ICreateStudyForm>()

  const studyCollectionType = watch('studyCollectionType')

  const setCollectionType = () => {
    setValue('studyCollectionType', value as StudyCollectionType)
  }

  const generateClassName = () => {
    const defaultClass = styles.methodCard
    if (disabled) {
      return `${defaultClass} ${styles.methodCardDisabled}`
    } else {
      if (studyCollectionType === value) {
        return `${defaultClass} ${styles.activeCard}`
      } else {
        return `${styles.methodCard}`
      }
    }
  }

  return (
    <button onClick={setCollectionType} type="button" className={generateClassName()}>
      <span className={styles.methodIcon}>{icon}</span>
      <span className={styles.methodLabel}>{label}</span>
    </button>
  )
}

export default DataCollectionSection
