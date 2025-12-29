import { Button, Loader } from '@mantine/core'
import styles from './modal.module.css'
import { useGetUserProjects } from '@/api-specs/hooks/useGetUserProjects'

type SelectProjectStepProps = {
  onAddNew: () => void
  onChooseTopic: () => void
  selectedProject: number | null
  setSelectedProject: (value: number) => void
}

function SelectProjectStep({ onAddNew, onChooseTopic, selectedProject, setSelectedProject }: SelectProjectStepProps) {
  const { data: projects, isLoading } = useGetUserProjects()

  const handleSelectProject = (id: number) => {
    setSelectedProject(id)
  }
  return (
    <div>
      <p className={styles.desc}>
        Projects help you organize your studies, create a new project or select an existing one.
      </p>

      <div className={styles.tabs}>
        <Button className={styles.selectedStep} c={'accent.6'} variant="transparent">
          Your projects
        </Button>
        <Button c={'accent.6'} variant="transparent" onClick={onAddNew}>
          Add new
        </Button>
      </div>

      <div>
        {isLoading ? (
          <Loader color="blue" type="dots" />
        ) : projects?.data.length === 0 ? (
          <div className={styles.emptyState}>
            <p>No projects yet</p>
          </div>
        ) : (
          <div className={styles.projects}>
            {projects?.data.map((project) => (
              <div
                onClick={() => handleSelectProject(project.id)}
                key={project.id}
                className={`${styles.project} ${selectedProject === project.id ? styles.selectedProject : ''}`}
              >
                <p className={styles.projectName}>{project.title}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className={styles.mainBtnContainer}>
        <Button bg="accent.6" onClick={onChooseTopic}>
          Choose topic
        </Button>
      </div>
    </div>
  )
}

export default SelectProjectStep
