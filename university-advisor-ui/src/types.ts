export type MessageRole = "user" | "assistant" | "system"

export type CheckpointStatus = "pass" | "fail" | "skip" | "pending"

export interface TraceStep {
  id: string
  checkpoint: number         // 1, 2, or 3
  label: string              // e.g. "RETRIEVAL DECISION"
  status: CheckpointStatus
  detail: string             // e.g. "Needs Retrieval: True"
  reasoning?: string         // The reasoning text from the agent
  docs_graded?: number       // How many docs were graded (checkpoint 2)
  docs_relevant?: number     // How many were relevant (checkpoint 2)
  web_search_triggered?: boolean
  retries_used?: number
  timestamp: Date
}

export interface Message {
  id: string
  role: MessageRole
  content: string
  timestamp: Date
  trace?: TraceStep[]        // Only bot messages have traces
  isLoading?: boolean        // True while streaming
  path?: string              // e.g. "retrieve → grade → generate"
}

export interface WindowMemoryItem {
  role: MessageRole
  content: string
}
