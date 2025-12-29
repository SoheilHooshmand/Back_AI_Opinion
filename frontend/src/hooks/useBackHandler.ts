import { useCanGoBack, useNavigate, useRouter } from '@tanstack/react-router'

const useBackHandler = () => {
  const canGoBack = useCanGoBack()
  const navigate = useNavigate()
  const router = useRouter()

  const backHandler = (fallbackUrl: string = '/home') => {
    if (canGoBack) {
      router.history.back()
    } else {
      navigate({
        to: fallbackUrl,
      })
    }
  }

  return backHandler
}

export default useBackHandler
