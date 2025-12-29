import * as yup from 'yup'

export const schema: yup.ObjectSchema<IPriceCalculatorForm> = yup.object({
  numQuestions: yup.string().required('Please enter number of questions'),
  aiModel: yup.string().required(),
  numSiliconPeople: yup.string().required('Please enter number of Silicon People'),
  questionFile: yup.mixed<File>().nullable(),
})

export interface IPriceCalculatorForm {
  numQuestions: string
  aiModel: string
  numSiliconPeople: string
  questionFile?: File | undefined | null
}

export type PriceCalculatorForm = yup.InferType<typeof schema>

export type ModalStep = 'select-project' | 'add-project' | 'choose-topic'

export const modelOptions = [
  { label: 'gpt-5.1', value: 'gpt-5.1' },
  { label: 'gpt-5', value: 'gpt-5' },
  { label: 'gpt-5-mini', value: 'gpt-5-mini' },
  { label: 'gpt-5-nano', value: 'gpt-5-nano' },
  { label: 'gpt-5-pro', value: 'gpt-5-pro' },
  { label: 'gpt-4.1', value: 'gpt-4.1' },
  { label: 'gpt-4.1-mini', value: 'gpt-4.1-mini' },
  { label: 'gpt-4.1-nano', value: 'gpt-4.1-nano' },
  { label: 'gpt-4o', value: 'gpt-4o' },
  { label: 'gpt-4o-mini', value: 'gpt-4o-mini' },
  { label: 'gpt-3.5-turbo', value: 'gpt-3.5-turbo' },
]
