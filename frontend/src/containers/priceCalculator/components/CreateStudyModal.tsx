import { Loader, Modal } from '@mantine/core'
import { useNavigate } from '@tanstack/react-router'
import { Suspense, lazy, useEffect, useState } from 'react'
import type { ModalStep } from '../utils'

const ChooseTopicStep = lazy(() => import('./ChooseTopicStep'))
const AddProjectStep = lazy(() => import('./AddProjectStep'))
const SelectProjectStep = lazy(() => import('./SelectProjectStep'))

type CreateStudyModalProps = {
  opened: boolean
  setOpened: (value: boolean) => void
}

const CreateStudyModal = ({ opened, setOpened }: CreateStudyModalProps) => {
  const [step, setStep] = useState<ModalStep>('select-project')

  const [selectedProject, setSelectedProject] = useState<number | null>(null)

  useEffect(() => {
    if (!opened) {
      setStep('select-project')
    }
  }, [opened])

  const navigate = useNavigate()
  const handleCreateStudy = () => {
    navigate({
      to: '/create-study',
      search: {
        projectId: String(selectedProject),
      },
    })
  }
  const titleObj = {
    'select-project': 'Add your study to a project',
    'add-project': 'Add your study to a project',
    'choose-topic': 'Choose your prefer topic',
  }

  return (
    <Modal
      title={titleObj[step]}
      opened={opened}
      onClose={() => setOpened(false)}
      centered
      radius="lg"
      styles={{
        title: {
          fontWeight: 'bold',
          fontSize: '24px',
        },
      }}
    >
      <Suspense fallback={<Loader color="blue" type="dots" />}>
        {step === 'select-project' && (
          <SelectProjectStep
            selectedProject={selectedProject}
            setSelectedProject={setSelectedProject}
            onAddNew={() => setStep('add-project')}
            onChooseTopic={() => setStep('choose-topic')}
          />
        )}
      </Suspense>

      <Suspense fallback={<Loader color="blue" type="dots" />}>
        {step === 'add-project' && (
          <AddProjectStep setSelectedProject={setSelectedProject} onNext={() => setStep('choose-topic')} />
        )}
      </Suspense>

      <Suspense fallback={<Loader color="blue" type="dots" />}>
        {step === 'choose-topic' && (
          <ChooseTopicStep value={selectedProject} onChange={setSelectedProject} onCreate={handleCreateStudy} />
        )}
      </Suspense>
    </Modal>
  )
}

export default CreateStudyModal
