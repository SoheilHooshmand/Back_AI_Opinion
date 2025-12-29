// types/project.types.ts

export interface Project {
  id: number
  title: string
  description: string
  status: 'draft' | 'running' | 'completed' | 'failed' // adjust based on your actual statuses
  created_at: string // ISO date string
  updated_at: string // ISO date string
  user: number // user ID
}

export type ProjectListResponse = {
  data: Array<Project>
  status: number
}

export interface CreateProjectResponse {
  data: CreateProjectResponseItem
  status: number
}

export interface CreateProjectResponseItem {
  title: string
  description: string
}
