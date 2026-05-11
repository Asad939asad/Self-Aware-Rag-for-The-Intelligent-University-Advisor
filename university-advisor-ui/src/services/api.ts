import { WindowMemoryItem } from "../types"

const API_BASE = ""
const MOCK_MODE = false // Set to false when backend is running

export interface ChatRequest {
  query: string
  window_memory: WindowMemoryItem[]
}

export interface CheckpointData {
  checkpoint: number
  label: string
  status: "pass" | "fail" | "skip"
  detail: string
  reasoning?: string
  docs_graded?: number
  docs_relevant?: number
  web_search_triggered?: boolean
  retries_used?: number
}

export interface ChatResponse {
  answer: string
  path: string
  trace: CheckpointData[]
  used_web_search: boolean
  retry_count: number
}

export const sendMessage = async (request: ChatRequest): Promise<ChatResponse> => {
  if (MOCK_MODE) {
    await new Promise(resolve => setTimeout(resolve, 1500))
    return {
      answer: "Based on the university catalog, CS-301 Advanced Algorithms requires CS-201 Data Structures as a prerequisite. The course is offered every Fall semester and carries 3 credit hours. The instructor is Dr. Ahmad Khan from the CS department.",
      path: "decide_retrieval → retrieve → grade_documents → prepare_context → generate → check_hallucination → END",
      trace: [
        { checkpoint: 1, label: "RETRIEVAL DECISION", status: "pass", 
          detail: "Needs Retrieval: True", 
          reasoning: "Query asks about specific course prerequisites requiring KB search." },
        { checkpoint: 2, label: "RELEVANCE GRADING", status: "pass", 
          detail: "3/4 documents relevant", docs_graded: 4, docs_relevant: 3,
          web_search_triggered: false },
        { checkpoint: 3, label: "HALLUCINATION CHECK", status: "pass", 
          detail: "No hallucinations detected", retries_used: 0 }
      ],
      used_web_search: false,
      retry_count: 0
    }
  }

  const response = await fetch(`${API_BASE}/chat`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(request)
  })
  
  if (!response.ok) {
    throw new Error(`API error: ${response.status}`)
  }
  
  return response.json()
}
