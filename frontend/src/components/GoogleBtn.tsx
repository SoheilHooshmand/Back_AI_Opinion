import { Button } from '@mantine/core'
import googleLogo from '/imgs/google.svg'

type Props = {
  onClick: () => void
}

const GoogleBtn = ({ onClick }: Props) => {
  return (
    <Button
      onClick={onClick}
      fullWidth
      variant="white"
      radius="lg"
      leftSection={<img src={googleLogo} alt="google logo" />}
    >
      Continue with Google
    </Button>
  )
}

export default GoogleBtn
