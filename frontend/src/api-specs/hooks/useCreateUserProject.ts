import { useMutation } from '@tanstack/react-query'
import { createProjectRequest } from '../api'
import type { UseMutationOptions } from '@tanstack/react-query'
import type { ApiAxiosResponse } from '../types/common/types'
import type { CreateProjectResponse } from '../types/response/userProjects'
import type { CreateProjectPayload } from '../types/payload/userProjects'

type CreateProjectMutationOptions = UseMutationOptions<
  ApiAxiosResponse<CreateProjectResponse>,
  Error,
  CreateProjectPayload
>

export function useCreateUserProject(options?: CreateProjectMutationOptions) {
  return useMutation<ApiAxiosResponse<CreateProjectResponse>, Error, CreateProjectPayload>({
    mutationFn: createProjectRequest,
    ...options,
  })
}
