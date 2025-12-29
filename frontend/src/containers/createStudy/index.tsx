import { Button } from '@mantine/core'
import { FormProvider, useForm } from 'react-hook-form'
import { yupResolver } from '@hookform/resolvers/yup'
import { useSearch } from '@tanstack/react-router'
import { createStudySchema } from '../utils'
import CostCalculator from './component/costCalculator/CostCalculator'
import DataCollectionInput from './component/dataCollectionInput/DataCollectionInput'
import DataCollectionSection from './component/dataCollectionType/DataCollection'
import RecruitParticipantsSection from './component/participant/RecruitParticipant'
import Summary from './component/summary'
import styles from './createStudy.module.css'
import type { ICreateStudyForm } from '../utils'

const CreateStudy = () => {
  const { projectId } = useSearch({ from: '/_authLayout/create-study' })
  console.log({ projectId })

  const form = useForm<ICreateStudyForm>({
    resolver: yupResolver(createStudySchema),
    defaultValues: {
      collectionType: 'link',
      studyName: '',
      internalStudyName: '',
      description: '',
      studyLink: '',
      studyCollectionFile: null,
      siliconParticipants: 0,
      location: 'us',
      screeningMode: null,
      screenerSet: '',
    },
  })

  const onSubmit = (values: ICreateStudyForm) => {
    console.log(values, projectId)
  }

  return (
    <>
      {/* ---------- Header ---------- */}
      <div className={styles.header}>
        <div>
          <h1 className={styles.title}>Set up your study</h1>
          <p className={styles.subtitle}>Use the calculator to estimate how much a study will cost to complete.</p>
        </div>

        <Button size="sm" variant="outline">
          Save draft
        </Button>
      </div>

      <div className={styles.layout}>
        {/* ---------- Main Column ---------- */}
        <FormProvider {...form}>
          <form onSubmit={form.handleSubmit(onSubmit)}>
            <div className={styles.main}>
              <DataCollectionSection />

              <DataCollectionInput />

              <RecruitParticipantsSection />

              <CostCalculator />

              {/* CTA */}
              {/* <div className={styles.actions}>
            <Button variant="default">Back</Button>
            <Button bg="accent.6">Continue</Button>
          </div> */}
            </div>
          </form>
        </FormProvider>

        {/* ---------- Sidebar ---------- */}
        <div className={styles.sidebar}>
          <Summary />
        </div>
      </div>
    </>
  )
}

export default CreateStudy
