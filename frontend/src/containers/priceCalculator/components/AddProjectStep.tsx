import { Button, TextInput } from '@mantine/core'
import { useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import styles from './modal.module.css'
import type { CreateProjectPayload } from '@/api-specs/types/payload/userProjects'
import { useCreateUserProject } from '@/api-specs/hooks/useCreateUserProject'

type AddProjectStepProps = {
  onNext: () => void
  setSelectedProject: (value: number) => void
}

function AddProjectStep({ onNext }: AddProjectStepProps) {
  const [newProjectName, setNewProjectName] = useState('')

  const { mutate: createProject, isPending } = useCreateUserProject()
  const queryClient = useQueryClient()

  const handleAddProject = () => {
    const payload: CreateProjectPayload = {
      title: newProjectName,
      description: '',
    }
    createProject(payload, {
      onSuccess: (res) => {
        console.log(res)
        queryClient.invalidateQueries({ queryKey: ['projects'] })
        onNext()
      },
    })
  }
  return (
    <div>
      <TextInput
        label="Name (Maximum 120 character)"
        value={newProjectName}
        onChange={(e) => setNewProjectName(e.target.value)}
        placeholder="Text field data"
        mb={16}
      />

      <div className={styles.mainBtnContainer}>
        <Button loading={isPending} bg="accent.6" onClick={handleAddProject} disabled={!newProjectName.trim()}>
          Add new project
        </Button>
      </div>
    </div>
  )
}

export default AddProjectStep
