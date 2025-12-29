import { Button, Loader, Select } from '@mantine/core'
import { useMemo } from 'react'
import styles from './modal.module.css'
import { useGetUserProjects } from '@/api-specs/hooks/useGetUserProjects'

type ChooseTopicStepProps = {
  value: number | null
  onChange: (value: number | null) => void
  onCreate: () => void
}

function ChooseTopicStep({ value, onCreate, onChange }: ChooseTopicStepProps) {
  const { data: projects, isLoading } = useGetUserProjects()

  const topicOptions = useMemo(() => {
    return (
      projects?.data.map((project) => ({
        label: project.title,
        value: project.id.toString(), // Select requires string
      })) ?? []
    )
  }, [projects])

  const handleSelectProject = (id: string) => {
    onChange(Number(id))
  }

  return (
    <div>
      <Select
        value={String(value)}
        onChange={(val) => handleSelectProject(val!)}
        label="Project"
        placeholder={isLoading ? 'Loading projects...' : 'Select project'}
        data={topicOptions}
        clearable
        disabled={isLoading}
        rightSection={isLoading ? <Loader size="xs" /> : null}
        rightSectionPointerEvents="none"
        mb={24}
      />

      <div className={styles.mainBtnContainer}>
        <Button bg={'accent.6'} disabled={!value} onClick={onCreate}>
          Create study
        </Button>
      </div>
    </div>
  )
}

export default ChooseTopicStep
