import type { AxiosResponse } from 'axios'

// sometime backend return data in envelope and make everything complicated and wrong

// i mean some time is like this . yes this is so bad
// export type ApiEnvelope<T> = T | { data: T }
// this envelope does not include when response is data
export type ApiEnvelope<T> = T

export type ApiAxiosResponse<T> = AxiosResponse<ApiEnvelope<T>>
