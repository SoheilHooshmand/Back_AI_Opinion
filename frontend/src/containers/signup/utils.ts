import * as yup from 'yup'

export const schema = yup.object({
  username: yup.string().required('Please enter username'),
  email: yup.string().email('Invalid email').required('Please enter email'),
  password1: yup.string().required('Please enter password'),
  password2: yup.string().required('Please enter password'),
})

export type SignupForm = yup.InferType<typeof schema>
