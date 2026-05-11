import warnings
warnings.filterwarnings("ignore")

from typing import TypedDict, List, Optional, Annotated
from langgraph.graph import StateGraph, END
from langchain_groq import ChatGroq
from langchain_core.documents import Document
from tools import retrieve_documents, web_search
import operator
import json
import os
from dotenv import load_dotenv

load_dotenv()

# Set to True only for Test Case 4 demonstration
HALLUCINATION_TEST_MODE = False 

import re

def safe_json_parse(text: str) -> dict:
    """Safely parse JSON from LLM response, handling markdown and extra text."""
    try:
        # First attempt: direct parse
        return json.loads(text.strip())
    except json.JSONDecodeError:
        # Second attempt: extract JSON block using regex
        match = re.search(r'(\{.*\})|(\[.*\])', text, re.DOTALL)
        if match:
            json_str = match.group(0)
            try:
                return json.loads(json_str)
            except json.JSONDecodeError:
                # Third attempt: clean common markdown issues
                clean_text = text.replace("```json", "").replace("```", "").strip()
                try:
                    return json.loads(clean_text)
                except json.JSONDecodeError:
                    return None
        return None

# --- STATE CLASS ---
class AgentState(TypedDict):
    query: str                          # The user's original question
    needs_retrieval: bool               # Checkpoint 1 result: does this need retrieval?
    retrieval_reasoning: str            # Why we decided to retrieve or not
    retrieved_docs: List[dict]          # Raw documents from vector store
    relevant_docs: List[dict]           # Filtered: only the relevant documents
    use_web_search: bool                # True if all docs were irrelevant
    web_results: List[dict]             # Results from Tavily web search
    generation_context: str             # The final context string used for generation
    response: str                       # The generated response
    hallucination_detected: bool        # True if hallucination check failed
    retry_count: int                    # How many times we've retried generation
    final_answer: str                   # The final answer returned to the user
    memory_context: str                 # Context from previous 2 exchanges
    trace_steps: List[dict]             # List of checkpoint trace data
    agent_path: str                     # String representing the logic flow

# --- LLM INITIALIZATION ---
llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    groq_api_key=os.getenv("GROQ_API")
)

# --- NODE 1: decide_retrieval ---
def decide_retrieval(state: AgentState) -> dict:
    query = state["query"]
    
    prompt = f"""You are a routing assistant for a university advisory system.
    
    Your job: Decide if the following query requires searching the university knowledge base 
    (course catalogs, academic policies, faculty directory) OR if it can be answered directly 
    from general knowledge or is a greeting/chitchat.
    
    Query: "{query}"
    
    Rules:
    - If the query is a greeting, introduction, or social message → NO retrieval needed
    - If the query asks about general concepts (e.g., "What does GPA stand for?") → NO retrieval needed
    - If the query is about a specific course, prerequisite, credit hours, schedule → YES retrieval needed
    - If the query is about university policies (grading, fees, attendance, withdrawal) → YES retrieval needed
    - If the query is about a specific faculty member → YES retrieval needed
    
    Respond in this EXACT JSON format (no other text):
    {{
      "needs_retrieval": true or false,
      "reasoning": "one sentence explanation"
    }}
    """
    
    response = llm.invoke(prompt)
    data = safe_json_parse(response.content)
    if data is None:
        data = {"needs_retrieval": True, "reasoning": "Parsing error, defaulting to retrieval"}
    
    checkpoint_data = {
        "checkpoint": 1,
        "label": "RETRIEVAL DECISION",
        "status": "pass" if data["needs_retrieval"] else "skip",
        "detail": f"Needs Retrieval: {data['needs_retrieval']}",
        "reasoning": data["reasoning"]
    }
    
    return {
        "needs_retrieval": data["needs_retrieval"],
        "retrieval_reasoning": data["reasoning"],
        "agent_path": "decide_retrieval",
        "trace_steps": [checkpoint_data]
    }

# --- NODE 2: retrieve ---
def retrieve(state: AgentState) -> dict:
    query = state["query"]
    print(f"\n[RETRIEVAL] Searching knowledge base for: '{query}'")
    
    docs = retrieve_documents.invoke({"query": query})
    
    print(f"  Retrieved {len(docs)} document chunks.")
    for i, doc in enumerate(docs):
        print(f"  Doc {i+1}: {doc['content'][:100]}... [Source: {doc['metadata'].get('source_file','unknown')}]")
    
    return {
        "retrieved_docs": docs,
        "agent_path": state["agent_path"] + " → retrieve"
    }

import asyncio

# --- NODE 3: grade_documents ---
async def grade_documents(state: AgentState) -> dict:
    query = state["query"]
    docs = state.get("retrieved_docs", [])
    relevant_docs = []
    
    if not docs:
        return {
            "relevant_docs": [],
            "use_web_search": True,
            "agent_path": state["agent_path"] + " → grade_documents (no docs)",
            "trace_steps": state["trace_steps"]
        }

    print(f"\n[CHECKPOINT 2 - RELEVANCE GRADING] Parallel batch grading {len(docs)} documents in 2 batches...")
    
    # Split into 3 batches of 5 (to process all 15 retrieved docs)
    batch1 = docs[:5]
    batch2 = docs[5:10]
    batch3 = docs[10:15]

    async def grade_batch(batch, batch_num):
        if not batch:
            return []
        
        print(f"  → Batch {batch_num}: Processing {len(batch)} docs via Groq...")
        batch_text = ""
        for i, doc in enumerate(batch):
            batch_text += f"\n--- DOCUMENT {i+1} ---\n{doc['content']}\n"
            
        prompt = f"""You are a relevance grader.
        Query: "{query}"
        Docs: {batch_text}
        
        CRITICAL: If a document contains information about a course, teacher, or university policy that MIGHT be related to the query, mark it as relevant. Be generous.
        
        Respond ONLY in JSON:
        {{ "results": [ {{ "index": 1, "relevant": true }}, ... ] }}
        """
        
        try:
            response = await llm.ainvoke(prompt)
            parsed = safe_json_parse(response.content)
            
            batch_relevant = []
            if parsed and "results" in parsed:
                for res in parsed["results"]:
                    idx = res.get("index", 0) - 1
                    if 0 <= idx < len(batch) and res.get("relevant"):
                        batch_relevant.append(batch[idx])
            
            print(f"  ✓ Batch {batch_num} Finished.")
            return batch_relevant
        except Exception as e:
            print(f"  × Batch {batch_num} Error: {e}")
            return []

    # Run batches in parallel
    results = await asyncio.gather(
        grade_batch(batch1, 1),
        grade_batch(batch2, 2),
        grade_batch(batch3, 3)
    )
    
    # Flatten results
    for batch_result in results:
        relevant_docs.extend(batch_result)
    
    relevant_count = len(relevant_docs)
    total_count = len(docs)
    
    checkpoint_data = {
        "checkpoint": 2,
        "label": "RELEVANCE GRADING",
        "status": "pass" if relevant_count > 0 else "fail",
        "detail": f"{relevant_count}/{total_count} documents relevant (Parallel Batched)",
        "docs_graded": total_count,
        "docs_relevant": relevant_count,
        "web_search_triggered": relevant_count == 0
    }
    
    return {
        "relevant_docs": relevant_docs,
        "use_web_search": relevant_count == 0,
        "agent_path": state["agent_path"] + " → grade_documents",
        "trace_steps": state["trace_steps"] + [checkpoint_data]
    }

# --- NODE 4: web_search_node ---
def web_search_node(state: AgentState) -> dict:
    query = state["query"]
    print(f"\n[WEB SEARCH FALLBACK] Searching web for: '{query}'")
    
    results = web_search.invoke({"query": query})
    
    print(f"  Found {len(results)} web results.")
    
    return {
        "web_results": results,
        "agent_path": state["agent_path"] + " → web_search_node"
    }

# --- NODE 5: prepare_context ---
def prepare_context(state: AgentState) -> dict:
    if state.get("use_web_search") and state.get("web_results"):
        context_parts = []
        for result in state["web_results"]:
            context_parts.append(f"[Web Source: {result.get('url', 'unknown')}]\n{result.get('content', '')}")
        context = "\n\n---\n\n".join(context_parts)
        print(f"\n[CONTEXT PREPARED] Using web search results as context.")
    elif state.get("relevant_docs"):
        context_parts = []
        for doc in state["relevant_docs"]:
            meta = doc["metadata"]
            source_label = f"[Source: {meta.get('source_file','?')} | Dept: {meta.get('department','?')}]"
            context_parts.append(f"{source_label}\n{doc['content']}")
        context = "\n\n---\n\n".join(context_parts)
        print(f"\n[CONTEXT PREPARED] Using {len(state['relevant_docs'])} relevant documents.")
    else:
        context = ""
        print(f"\n[CONTEXT PREPARED] No context available.")
    
    return {
        "generation_context": context,
        "agent_path": state["agent_path"] + " → prepare_context"
    }

# --- NODE 6: generate ---
def generate(state: AgentState) -> dict:
    query = state["query"]
    context = state.get("generation_context", "")
    retry_count = state.get("retry_count", 0)
    
    print(f"\n[GENERATION] Generating response (attempt {retry_count + 1})...")
    if context:
        print(f"  → Using {len(context)} characters of retrieved context.")
    else:
        print(f"  → No context available, using general knowledge.")
    
    memory_context = state.get("memory_context", "")
    
    if context:
        prompt = f"""You are a helpful university course advisory assistant for XYZ National University.
      
      Previous conversation context:
      {memory_context}
      
      CRITICAL INSTRUCTIONS:
      1. EXHAUSTIVE LISTING: You must list EACH AND EVERY course found in the context. Search the context thoroughly for every mention of a course code or title.
      2. CLEAN FORMATTING: Do NOT use asterisks (*) for bullets or bolding. Use numbered headers (e.g., 1., 2., 3.) for main courses and plain text for details.
      3. STRUCTURE: For each course, provide: Name, Credits, Prerequisites, Instructor, and a brief Description.
      4. ACCURACY: If a course mentions 'CS-501' but the context says 'Advanced Machine Learning', use the title from the context.
      
      Context:
      {context}
      
      Student Question: {query}
      
      Answer clearly and professionally:
      """
    else:
        prompt = f"""You are a helpful university course advisory assistant.
      
      Previous conversation context:
      {memory_context}
      
      Answer the following question from your general knowledge.
      
      Question: {query}
      
      Provide a clear and helpful answer:
      """
    
    response = llm.invoke(prompt)
    generated = response.content
    
    print(f"  Generated response: {generated[:200]}...")
    
    return {
        "response": generated,
        "agent_path": state["agent_path"] + " → generate"
    }

# --- NODE 7: check_hallucination ---
def check_hallucination(state: AgentState) -> dict:
    response = state["response"]
    context = state.get("generation_context", "")
    retry_count = state.get("retry_count", 0)
    use_web = state.get("use_web_search", False)
    
    print(f"\n[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt {retry_count + 1})")
    
    # Force hallucination detection for demonstration purposes
    if HALLUCINATION_TEST_MODE and retry_count == 0:
        print("  [TEST MODE] Forcing hallucination detection for demonstration.")
        return {
            "hallucination_detected": True,
            "retry_count": 1,
            "hallucination_explanation": "TEST MODE: Forced hallucination for demonstration."
        }
        
    # Skip check if no retrieval was used (direct general knowledge answer)
    if not state.get("needs_retrieval", True):
      print("  → No retrieval was used. Skipping hallucination check.")
      return {
        "hallucination_detected": False,
        "final_answer": response
      }
    
    # Skip check if no context is available
    if not context:
      print("  → No context available. Skipping hallucination check.")
      return {
        "hallucination_detected": False,
        "final_answer": response
      }
    
    # Use DIFFERENT strictness levels based on source type
    if use_web:
      strictness_instruction = """
  This response was generated from WEB SEARCH RESULTS, not official documents.
  Apply LENIENT checking:
  - Only flag it if the response invents completely fabricated facts with 
    no basis whatsoever in the web results.
  - Reasonable inference, summarization, and synthesis from web results is ALLOWED.
  - Minor extrapolation (e.g., inferring a rank number from ranking context) is OK.
  - Do NOT flag responses that reasonably summarize or paraphrase web results.
  - Only return hallucination_detected=true if the response contains a specific 
    claim that directly contradicts the web results."""
    else:
      strictness_instruction = """
  This response was generated from OFFICIAL UNIVERSITY DOCUMENTS.
  Apply STRICT but INTELLIGENT checking:
  - Flag any specific entity (name, fee, course code, grade) that is NOT present in the context.
  - For NUMBERS and COUNTS:
    a) If a number (like a fee or credit hour) is explicitly stated in the response, verify it matches the context.
    b) If a total count is provided (e.g., 'There are 8 courses'), do NOT flag it if the items being counted are all present and verified in the context.
  - Do NOT flag the university name "XYZ National University" as a hallucination.
  - Do NOT flag polite conversational phrases or general framing.
  - Do NOT flag minor rephrasing or summarization of document content."""
    
    prompt = f"""You are a hallucination detector for a university advisory AI.
    
    Student Question: "{state['query']}"
    
  {strictness_instruction}
  
  Context:
  ---
  {context}
  ---
  
  Generated Response:
  ---
  {response}
  ---
  
  Respond in this EXACT JSON format (no other text):
  {{
    "hallucination_detected": true or false,
    "explanation": "specific invented fact found, or 'none' if clean"
  }}
  """
    
    result = llm.invoke(prompt)
    data = safe_json_parse(result.content)
    if data is None:
      data = {"hallucination_detected": False, "explanation": "Parsing error, assuming clean"}
    
    print(f"  Hallucination detected: {data['hallucination_detected']}")
    print(f"  Explanation: {data['explanation']}")
    
    checkpoint_data = {
        "checkpoint": 3,
        "label": "HALLUCINATION CHECK",
        "status": "fail" if data["hallucination_detected"] else "pass",
        "detail": data["explanation"],
        "retries_used": retry_count
    }
    
    if data["hallucination_detected"]:
      new_retry_count = retry_count + 1
      print(f"  → Hallucination found! Retry count: {new_retry_count}")
      
      return {
        "hallucination_detected": True,
        "retry_count": new_retry_count,
        "agent_path": state["agent_path"] + " → check_hallucination",
        "trace_steps": state["trace_steps"] + [checkpoint_data]
      }
    else:
      return {
        "hallucination_detected": False,
        "final_answer": response,
        "agent_path": state["agent_path"] + " → check_hallucination → END",
        "trace_steps": state["trace_steps"] + [checkpoint_data]
      }

# --- NODE 8: direct_answer ---
def direct_answer(state: AgentState) -> dict:
    query = state["query"]
    memory_context = state.get("memory_context", "")
    
    print(f"\n[DIRECT ANSWER] No retrieval needed. Answering from general knowledge.")
    
    prompt = f"""You are a friendly and helpful university course advisory assistant.
    
    Previous conversation context:
    {memory_context}
    
    Answer the following message naturally and helpfully.
    
    Message: {query}
    """
    
    response = llm.invoke(prompt)
    print(f"  Response: {response.content[:200]}...")
    
    return {
        "final_answer": response.content,
        "needs_retrieval": False,
        "agent_path": state["agent_path"] + " → direct_answer → END"
    }

# --- NODE 9: max_retries_exceeded ---
MAX_RETRIES = 2

def max_retries_exceeded(state: AgentState) -> dict:
    print(f"\n[MAX RETRIES EXCEEDED] Could not generate a verified response after {MAX_RETRIES} attempts.")
    disclaimer = (
        "I was unable to generate a verified response for your query. "
        "The information I found may be incomplete or inconsistent. "
        "Please contact the university directly or visit the official university portal for accurate information."
    )
    return {
        "final_answer": disclaimer,
        "agent_path": state["agent_path"] + " → max_retries_exceeded → END"
    }

# --- CONDITIONAL EDGE FUNCTIONS ---
def route_after_retrieval_decision(state: AgentState) -> str:
    if state["needs_retrieval"]:
        return "retrieve"
    else:
        return "direct_answer"

def route_after_grading(state: AgentState) -> str:
    if state["use_web_search"]:
        return "web_search_node"
    else:
        return "prepare_context"

def route_after_hallucination_check(state: AgentState) -> str:
    if not state["hallucination_detected"]:
        return END
    elif state.get("retry_count", 0) >= MAX_RETRIES:
        return "max_retries_exceeded"
    else:
        return "generate"

# --- BUILD THE STATEGRAPH ---
def build_graph():
    graph = StateGraph(AgentState)
    
    graph.add_node("decide_retrieval", decide_retrieval)
    graph.add_node("retrieve", retrieve)
    graph.add_node("grade_documents", grade_documents)
    graph.add_node("web_search_node", web_search_node)
    graph.add_node("prepare_context", prepare_context)
    graph.add_node("generate", generate)
    graph.add_node("check_hallucination", check_hallucination)
    graph.add_node("direct_answer", direct_answer)
    graph.add_node("max_retries_exceeded", max_retries_exceeded)
    
    graph.set_entry_point("decide_retrieval")
    
    graph.add_edge("retrieve", "grade_documents")
    graph.add_edge("web_search_node", "prepare_context")
    graph.add_edge("prepare_context", "generate")
    graph.add_edge("generate", "check_hallucination")
    graph.add_edge("max_retries_exceeded", END)
    graph.add_edge("direct_answer", END)
    
    graph.add_conditional_edges(
        "decide_retrieval",
        route_after_retrieval_decision,
        {
            "retrieve": "retrieve",
            "direct_answer": "direct_answer"
        }
    )
    
    graph.add_conditional_edges(
        "grade_documents",
        route_after_grading,
        {
            "web_search_node": "web_search_node",
            "prepare_context": "prepare_context"
        }
    )
    
    graph.add_conditional_edges(
        "check_hallucination",
        route_after_hallucination_check,
        {
            END: END,
            "max_retries_exceeded": "max_retries_exceeded",
            "generate": "generate"
        }
    )
    
    return graph.compile()

app = build_graph()
