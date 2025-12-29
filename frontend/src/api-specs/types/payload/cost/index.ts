export interface TokenCostPayload {
  model_name: string

  num_silicon_people: number

  questions_list?: Array<string>

  questions_file?: File
}
