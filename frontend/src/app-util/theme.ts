import { createTheme } from '@mantine/core'

const theme = createTheme({
  defaultRadius: 'md',
  colors: {
    primary: [
      '#EDF2ED',
      '#E1EDE1',
      '#BED4BE',
      '#9EBA9E',
      '#81A181',
      '#658765',
      '#4D6E4D',
      '#375437',
      '#264026',
      '#1C331C',
    ],
    accent: [
      '#F2F9FF',
      '#D5EDFF',
      '#B8E0FF',
      '#9AD3FF',
      '#7DC7FF',
      '#5DA6DD',
      '#4186BB',
      '#2A6999',
      '#184E77',
      '#0B3555',
    ],

    neutral: [
      '#F5F5FA',
      '#E4E5F1',
      '#CFD0E2',
      '#B3B5CC',
      '#9496B8',
      '#6C6F93',
      '#47496B',
      '#32344B',
      '#1D1E30',
      '#0A0B12',
    ],
    info: [
      '#E6F7FF',
      '#BAE7FF',
      '#91D5FF',
      '#69C0FF',
      '#40A9FF',
      '#1890FF',
      '#096DD9',
      '#0050B3',
      '#003A8C',
      '#002766',
    ],
  },

  primaryColor: 'primary',
})

export default theme
