import { Button, Loader, Paper, TextInput } from '@mantine/core'
import { IconFile } from '@tabler/icons-react'
import { Controller, useFormContext } from 'react-hook-form'
import { Suspense, lazy } from 'react'
import styles from './dataCollectionInput.module.css'
import type { ICreateStudyForm } from '@/containers/utils'

const Dropzone = lazy(() => import('@mantine/dropzone').then((mod) => ({ default: mod.Dropzone })))

export type DataCollectionInputType = 'external' | 'file'

function DataCollectionInput() {
  const {
    control,
    register,
    watch,
    formState: { errors },
  } = useFormContext<ICreateStudyForm>()

  const collectionType = watch('collectionType')

  const onSampleClick = (event: React.MouseEvent<HTMLButtonElement>) => {
    event.preventDefault()
    event.stopPropagation()
    const sampleFile = 'assets/samples/question.csv'
    const link = document.createElement('a')
    link.href = sampleFile
    link.download = 'question.csv'
    link.click()
  }

  return (
    <Paper radius="lg" p="md" className={styles.wrapper}>
      <h3 className={styles.title}>Data collection</h3>

      {/* ---------- External URL ---------- */}
      {collectionType === 'link' && (
        <>
          <label className={styles.label}>What’s the URL of your study?</label>
          <TextInput {...register('studyLink')} placeholder="Text field data" error={errors.studyLink?.message} />
        </>
      )}

      {/* ---------- File upload ---------- */}
      {collectionType === 'file' && (
        <>
          <label className={styles.label}>Upload files</label>
          <p className={styles.helper}>Select and upload the files of your choice</p>
          <Suspense fallback={<Loader />}>
            <Controller
              control={control}
              name="studyCollectionFile"
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
                        <div className={styles.dropzoneInner}>
                          <IconFile />
                          <p className={styles.dropTitle}>Choose a file or drag & drop it here</p>
                          <p className={styles.dropDesc}>CSV and XLSX formats, up to 50MB</p>
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
          </Suspense>
        </>
      )}
    </Paper>
  )
}

export default DataCollectionInput
