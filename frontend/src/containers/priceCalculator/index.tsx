import { yupResolver } from '@hookform/resolvers/yup'
import { Controller, useForm } from 'react-hook-form'

import { Button, Flex, Paper, Select, TextInput } from '@mantine/core'

import { Dropzone } from '@mantine/dropzone'
import { IconCpu, IconFile, IconInfoCircle, IconMessageReply, IconScreenShare, IconUsers } from '@tabler/icons-react'
import { useState } from 'react'
import CreateStudyModal from './components/CreateStudyModal'
import styles from './priceCalculator.module.css'
import { modelOptions, schema } from './utils'
import type { IPriceCalculatorForm } from './utils'
import useBackHandler from '@/hooks/useBackHandler'
import { useCalculateTokenCostRequest } from '@/api-specs/hooks/useCalculateTokenCostRequest'

function PricingCalculator() {
  const [opened, setOpened] = useState(false)

  const backHandler = useBackHandler()

  const {
    mutate: calculateTokenCost,
    data: tokenCostData,
    isPending: isCalculatingPrice,
  } = useCalculateTokenCostRequest()

  const {
    handleSubmit,
    register,
    control,
    formState: { errors },
  } = useForm<IPriceCalculatorForm>({
    resolver: yupResolver(schema),
    defaultValues: {
      numQuestions: '',
      aiModel: '',
      numSiliconPeople: '',
      questionFile: undefined,
    },
  })

  const onSubmit = (values: IPriceCalculatorForm) => {
    const formData = new FormData()
    if (values.questionFile) {
      formData.append('questions_file', values.questionFile)
    }
    formData.append('model_name', values.aiModel)
    formData.append('num_silicon_people', values.numSiliconPeople)

    calculateTokenCost(formData)
  }

  const onSampleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    event.stopPropagation()
    const sampleFile = 'assets/samples/test_cost.csv'
    const link = document.createElement('a')
    link.href = sampleFile
    link.download = 'test_cost.csv'
    link.click()
  }

  console.log('token cost', tokenCostData)

  return (
    <>
      <div className={styles.backBtn} onClick={() => backHandler('/home')}>
        <IconMessageReply /> Back
      </div>

      <h1 className={styles.pageTitle}>Pricing calculator</h1>
      <p className={styles.pageSubtitle}>Use the calculator to estimate how much a study will cost to complete.</p>

      <Paper radius="lg">
        <form className={styles.box} onSubmit={handleSubmit(onSubmit)}>
          <div className={styles.inputsBox}>
            <Flex gap={{ base: 8, sm: 0 }} direction={{ base: 'column', sm: 'row' }} mb={24}>
              <div className={styles.inputDesc}>
                <div className={styles.labelWrapper}>
                  <p className={styles.label}>
                    <IconUsers size={14} />
                    Number of questions
                  </p>
                  <IconInfoCircle size={14} color="gray" />
                </div>
                <p className={styles.desc}>Total number of questions to ask Silicon Users</p>
              </div>

              <div className={styles.input}>
                <TextInput
                  placeholder="Text field data"
                  {...register('numQuestions')}
                  error={errors.numQuestions?.message}
                />
              </div>
            </Flex>

            <Flex gap={{ base: 8, sm: 0 }} direction={{ base: 'column', sm: 'row' }} mb={24}>
              <div className={styles.inputDesc}>
                <div className={styles.labelWrapper}>
                  <p className={styles.label}>
                    <IconCpu size={14} />
                    The AI model used
                  </p>
                  <IconInfoCircle size={14} color="gray" />
                </div>
                <p className={styles.desc}>The artificial intelligence model used in your project</p>
              </div>

              <div className={styles.input}>
                <Controller
                  control={control}
                  name="aiModel"
                  render={({ field, fieldState }) => (
                    <Select
                      placeholder="ai model"
                      data={modelOptions}
                      value={field.value}
                      onChange={field.onChange}
                      error={fieldState.error?.message}
                    />
                  )}
                />
              </div>
            </Flex>

            <Flex gap={{ base: 8, sm: 0 }} direction={{ base: 'column', sm: 'row' }} mb={24}>
              <div className={styles.inputDesc}>
                <div className={styles.labelWrapper}>
                  <p className={styles.label}>
                    <IconScreenShare size={14} />
                    Number of Silicon People
                  </p>
                  <IconInfoCircle size={14} color="gray" />
                </div>
                <p className={styles.desc}>The categories you defined in your project</p>
              </div>

              <div className={styles.input}>
                <TextInput
                  error={errors.numSiliconPeople?.message}
                  placeholder="Text field data"
                  {...register('numSiliconPeople')}
                />
              </div>
            </Flex>

            <Flex gap={{ base: 8, sm: 0 }} direction={'column'} mb={24}>
              <div className={styles.inputDesc}>
                <div className={styles.labelWrapper}>
                  <p className={styles.label}>
                    <IconFile size={14} />
                    Question File
                  </p>
                  <IconInfoCircle size={14} color="gray" />
                </div>
                <p className={styles.desc}>The questions you define to ask in your project</p>
              </div>

              <div className={styles.input}>
                <Controller
                  control={control}
                  name="questionFile"
                  render={({ field }) => {
                    const file = field.value

                    return (
                      <>
                        {!file ? (
                          <Dropzone
                            onDrop={(files) => field.onChange(files[0])}
                            maxSize={10 * 1024 * 1024}
                            accept={['text/csv', 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet']}
                            className={styles.dropzone}
                          >
                            <div className={styles.inner}>
                              <div className={styles.icon}>
                                <IconFile />
                              </div>

                              <p className={styles.title}>Choose a file or drag & drop it here</p>

                              <p className={styles.subtitle}>CSV and XLSX formats, up to 50MB</p>

                              <div className={styles.actions}>
                                <Button variant="outline" radius="xl">
                                  Browse file
                                </Button>

                                <Button radius="xl" onClick={(e) => onSampleClick(e)}>
                                  sample
                                </Button>
                              </div>
                            </div>
                          </Dropzone>
                        ) : (
                          <div className={styles.uploaded}>
                            <div className={styles.fileInfo}>
                              <IconFile />
                              <div>
                                <p className={styles.fileName}>{file.name}</p>
                                <p className={styles.fileSize}>{(file.size / 1024).toFixed(1)} KB</p>
                              </div>
                            </div>

                            <Button variant="subtle" color="red" onClick={() => field.onChange(null)}>
                              Remove
                            </Button>
                          </div>
                        )}
                      </>
                    )
                  }}
                />
              </div>
            </Flex>
          </div>
          <div className={styles.priceBox}>
            {tokenCostData?.data?.cost_usd?.total && (
              <div className={styles.costCard}>
                <p className={styles.costLabel}>Total cost</p>
                <p className={styles.costValue}>{tokenCostData?.data?.cost_usd?.total}</p>
              </div>
            )}

            <Button loading={isCalculatingPrice} fullWidth bg={'accent.6'} type="submit" color="white">
              Submit and calculate
            </Button>

            <Button
              disabled={!tokenCostData?.data?.cost_usd?.total}
              variant="outline"
              fullWidth
              onClick={() => setOpened(true)}
            >
              Create Study
            </Button>
          </div>
        </form>
      </Paper>
      <CreateStudyModal opened={opened} setOpened={setOpened} />
    </>
  )
}

export default PricingCalculator
