import * as yup from 'yup'

export const schema = yup.object({
  email: yup.string().email('Invalid email').required('Please enter email'),
  password: yup.string().required('Please enter password'),
  remember: yup.boolean().default(false),
})

export type LoginForm = yup.InferType<typeof schema>
