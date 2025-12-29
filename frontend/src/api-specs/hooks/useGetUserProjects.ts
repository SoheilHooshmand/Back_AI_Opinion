import { useQuery } from '@tanstack/react-query'
import { fetchUserProjectsRequest } from '../api'

export function useGetUserProjects() {
  return useQuery({
    queryKey: ['projects'],
    queryFn: () => fetchUserProjectsRequest(),
    select: (res) => res.data,
  })
}
