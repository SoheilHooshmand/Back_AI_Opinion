import { createFileRoute } from '@tanstack/react-router'
import CreateStudy from '@/containers/createStudy'

type CreateStudySearchParams = {
  projectId: string
}

export const Route = createFileRoute('/_authLayout/create-study')({
  component: RouteComponent,
  validateSearch: (search: Record<string, unknown>): CreateStudySearchParams => {
    return {
      projectId: search.projectId as string,
    }
  },
})

function RouteComponent() {
  return (
    <div>
      <CreateStudy />
    </div>
  )
}
