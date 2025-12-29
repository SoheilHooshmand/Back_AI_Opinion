interface StudyResultRow {
  id: string
  question: string
  siliconUserId: string
  siliconAnswer: string
  dataAnswer: string
  accuracy: number
}

export const mockResults: Array<StudyResultRow> = Array.from({ length: 42 }).map((_, i) => ({
  id: String(i + 1),
  question: 'Who did silicon user vote for...',
  siliconUserId: `667c93d28b51b98ecedb98a${i}`,
  siliconAnswer: i % 2 === 0 ? 'Trump' : 'Biden',
  dataAnswer: i % 2 === 0 ? 'Biden' : 'Trump',
  accuracy: i % 2 === 0 ? 0 : 100,
}))
