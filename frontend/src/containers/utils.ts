import * as yup from 'yup'

export type StudyCollectionType = 'survey' | 'decision_making' | 'writing' | 'interview' | 'ai-task' | 'none'

export const createStudySchema: yup.ObjectSchema<ICreateStudyForm> = yup.object({
  collectionType: yup.mixed<'link' | 'file'>().required(),
  studyName: yup.string().required(),
  internalStudyName: yup.string(),
  description: yup.string(),
  studyLink: yup.string(),
  studyCollectionType: yup.mixed<StudyCollectionType>(),
  studyCollectionFile: yup.mixed<File>().nullable(),
  siliconParticipants: yup.mixed<number>().nullable(),
  location: yup.mixed<'us' | 'ca'>().oneOf(['us', 'ca']).nullable(),
  screeningMode: yup.mixed<'new' | 'saved'>().oneOf(['new', 'saved']).nullable(),
  screenerSet: yup.string(),
})

export interface ICreateStudyForm {
  collectionType: 'link' | 'file'
  studyName: string
  internalStudyName?: string
  description?: string
  studyCollectionType?: StudyCollectionType
  studyLink?: string
  studyCollectionFile?: File | undefined | null
  siliconParticipants?: number | null
  location?: 'us' | 'ca' | null
  screeningMode?: 'new' | 'saved' | null
  screenerSet?: string
}
