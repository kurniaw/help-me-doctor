export type UrgencyLevel = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'

export interface UserLocation {
  lat: number
  lng: number
}

export type Role = 'user' | 'assistant'

export interface Message {
  id: string
  role: Role
  content: string
  urgency?: UrgencyLevel
  pathway?: string
  timestamp: Date
}

export interface StreamChunk {
  type: 'chunk' | 'done' | 'error'
  content: string
  urgency?: UrgencyLevel
  pathway?: string
}
