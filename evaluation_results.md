# Self-RAG Agent — Evaluation Results
**Agent:** University Course Advisory Agent  
**University:** XYZ National University  
**Model:** gemini-flash-latest
**Vector DB:** ChromaDB  
**Embeddings:** sentence-transformers/all-MiniLM-L6-v2  

---

## Test Case 1: No Retrieval Needed (Greeting)

**Query:** "Hello! I am a new student. Can you help me navigate university resources?"

**Expected Path:**  
decide_retrieval → direct_answer → END  
Reasoning: This is a greeting/social message. No university-specific data is needed.

**Expected Behavior:**  
- needs_retrieval = False  
- Agent answers directly from general knowledge  
- Vector database is NOT queried  

**Actual Console Trace:**
```text
[CHECKPOINT 1 - RETRIEVAL DECISION]
  Query: Hello! I am a new student. Can you help me navigate university resources?
  Needs Retrieval: False
  Reasoning: The query is a greeting and a general request for assistance, which does not require specific university data at this stage.

[DIRECT ANSWER] No retrieval needed. Answering from general knowledge.
  Response: Hello! Welcome to the university—we are so happy to have you here! Starting out can feel a little overwhelming, but don't worry, you’ll get the hang of it in no time. I’d be more than happy to help you get settled.

To point you in the right direction, could you tell me a little bit about what you’re looking for? For example, are you trying to:

*   **Find academic support?** (Like the library, writing centers, or tutoring services)
*   **Get tech help?** (Accessing your student email, Wi-Fi, or the student portal)
*   **Learn about student life?** (Clubs, sports, or campus events)
*   **Locate administrative offices?** (Financial aid, registrar, or health services)

If you aren't sure where to start, I can also give you a quick "new student checklist" of the most important places to bookmark. Just let me know what’s on your mind!
```

**Final Answer:**
Hello! Welcome to the university—we are so happy to have you here! Starting out can feel a little overwhelming, but don't worry, you’ll get the hang of it in no time. I’d be more than happy to help you get settled.
...

**Verdict:** ✅ PASS

---

## Test Case 2: Retrieval Needed — Documents Relevant

**Query:** "Which professor is teaching EE-201 and EE-102?"

**Expected Path:**  
decide_retrieval → retrieve → grade_documents → prepare_context → generate → check_hallucination → END

**Expected Behavior:**  
- needs_retrieval = True  
- Documents from EE catalog retrieved  
- At least 1 document graded relevant  
- Response generated from relevant docs  
- Hallucination check passes  

**Actual Console Trace:**
```text
[CHECKPOINT 1 - RETRIEVAL DECISION]
  Query: Which professor is teaching EE-201 and EE-102?
  Needs Retrieval: True
  Reasoning: The query asks for specific instructors for particular courses in the electrical engineering department, which requires searching the course catalog.

[RETRIEVAL] Searching knowledge base for: 'Which professor is teaching EE-201 and EE-102?'
  Retrieved 4 document chunks.
  Doc 1: relevant=True | The document chunk explicitly lists Prof. zma afiq as the instructor for EE-102 and Dr. amran hah as the instructor for EE-201.
  Doc 2: relevant=True | The document chunk identifies the instructor for EE-102 as missing/not provided, but it confirms the existence of the course.
  Result: 2/4 documents are relevant.

[CONTEXT PREPARED] Using 2 relevant documents.

[GENERATION] Generating response (attempt 1)...
  Generated response: EE-201 is taught by Dr. amran hah, and EE-102 is taught by Prof. zma afiq.

[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt 1)
  Hallucination detected: False
  Explanation: none
```

**Final Answer:**
EE-201 is taught by Dr. amran hah, and EE-102 is taught by Prof. zma afiq.

**Verdict:** ✅ PASS

---

## Test Case 3: Web Search Fallback Triggered

**Query:** "What is the current QS world university ranking of XYZ National University?"

**Expected Path:**  
decide_retrieval → retrieve → grade_documents (all irrelevant) → web_search_node → prepare_context → generate → check_hallucination → END

**Expected Behavior:**  
- needs_retrieval = True  
- Retrieved docs are about courses/policies, NOT about world rankings  
- All docs graded irrelevant  
- use_web_search = True  
- Tavily web search fires  
- Answer generated from web results  

**Actual Console Trace:**
```text
[CHECKPOINT 1 - RETRIEVAL DECISION]
  Query: What is the current QS world university ranking of XYZ National University?
  Needs Retrieval: True
  Reasoning: The query asks for specific institutional data regarding the university's current ranking, which is typically maintained in official records or external ranking databases.

[RETRIEVAL] Searching knowledge base for: 'What is the current QS world university ranking of XYZ National University?'
  Retrieved 4 document chunks.
  Result: 0/4 documents are relevant.
  → All documents irrelevant. Will trigger web search fallback.

[WEB SEARCH FALLBACK] Searching web for: 'What is the current QS world university ranking of XYZ National University?'
  Found 3 web results.

[CONTEXT PREPARED] Using web search results as context.

[GENERATION] Generating response (attempt 1)...
  Generated response: The provided context does not contain information regarding the QS world university ranking of XYZ National University.

[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt 1)
  Hallucination detected: False
  Explanation: none
```

**Final Answer:**
The provided context does not contain information regarding the QS world university ranking of XYZ National University.

**Verdict:** ✅ PASS

---

## Test Case 4: Hallucination Detected — Retry Mechanism

**Query:** "List the complete details of all 12 CS courses including their exact course codes, credit hours, prerequisites, fees per credit hour, instructor names, office locations, and semester availability"

**Expected Path:**  
decide_retrieval → retrieve → grade_documents → prepare_context → generate → check_hallucination (FAIL) → generate (retry) → check_hallucination → END or max_retries_exceeded

**Expected Behavior:**  
- Retrieval needed (university-specific course data)  
- Generation attempts to fulfill the query but may lack some details  
- Hallucination check fires (or test mode forces it)  
- retry_count increments  
- Agent retries and produces clean answer or disclaimer  

**Actual Console Trace:**
```text
[CHECKPOINT 1 - RETRIEVAL DECISION]
  Query: List the complete details of all 12 CS courses including their exact course codes, credit hours, prerequisites, fees per credit hour, instructor names, office locations, and semester availability
  Needs Retrieval: True
  Reasoning: The query asks for extensive and specific course details, which requires retrieving information from the computer science department's course catalog.

[RETRIEVAL] Searching knowledge base for: 'List the complete details of all 12 CS courses...'
  Retrieved 4 document chunks.
  Result: 3/4 documents are relevant.

[CONTEXT PREPARED] Using 3 relevant documents.

[GENERATION] Generating response (attempt 1)...
  Generated response: I cannot provide the complete details you requested because the provided context does not contain information for all 12 courses...

[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt 1)
  [TEST MODE] Forcing hallucination detection for demonstration.

[GENERATION] Generating response (attempt 2)...
  Generated response: I cannot provide the complete details you requested because the provided context does not contain information for all 12 courses...

[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt 2)
  Hallucination detected: False
  Explanation: none
```

**Final Answer:**
The provided context contains information for the following courses:
* CS-101: Intro to Programming (Dr. Ahmed Raza)
* CS-102: Object Oriented Programming (Dr. Ahmed Raza)
* CS-201: Data Structures and Algorithms (Dr. Ahmed Raza)
* CS-202: Database Systems (Dr. Farhan Qureshi)
... (The provided context does not contain information for the remaining courses or fees).

**Verdict:** ✅ PASS (Retry mechanism demonstrated via Test Mode)

---

## Test Case 5: Creative Test — Academic Policy Query

**Query:** "What is the minimum CGPA a student needs to maintain to avoid academic probation at XYZ National University?"

**Expected Path:**  
decide_retrieval → retrieve → grade_documents → prepare_context → generate → check_hallucination → END

**Expected Behavior:**  
- Retrieval needed (university-specific policy)  
- University_Academic_Policies.pdf chunks retrieved  
- Relevant chunks about GPA/probation graded as relevant  
- Clean answer generated from policy document  
- Hallucination check passes (updated rules allow university name)  

**Actual Console Trace:**
```text
[CHECKPOINT 1 - RETRIEVAL DECISION]
  Query: What is the minimum CGPA a student needs to maintain to avoid academic probation at XYZ National University?
  Needs Retrieval: True
  Reasoning: The query asks for specific university policy regarding academic probation and CGPA requirements, which requires searching the academic policies document.

[RETRIEVAL] Searching knowledge base for: 'What is the minimum CGPA a student needs to maintain to avoid academic probation at XYZ National University?'
  Retrieved 4 document chunks.
  Doc 1: relevant=True | The document explicitly states that students are placed on academic probation if their CGPA falls below 1.50 for two consecutive semesters.
  Result: 1/4 documents are relevant.

[CONTEXT PREPARED] Using 1 relevant documents.

[GENERATION] Generating response (attempt 1)...
  Generated response: To avoid academic probation at XYZ National University, a student must ensure their CGPA does not fall below 1.50 for two consecutive semesters.

[CHECKPOINT 3 - HALLUCINATION CHECK] (attempt 1)
  Hallucination detected: False
  Explanation: none
```

**Final Answer:**
To avoid academic probation at XYZ National University, a student must ensure their CGPA does not fall below 1.50 for two consecutive semesters.

**Verdict:** ✅ PASS

---

## Summary Table

| # | Scenario | Query (short) | Path Taken | Result |
|---|---|---|---|---|
| 1 | No retrieval | Greeting | direct_answer | ✅ PASS |
| 2 | Retrieval + relevant | EE professors | retrieve→grade→generate | ✅ PASS |
| 3 | Web search fallback | World ranking | retrieve→grade→web→generate | ✅ PASS |
| 4 | Hallucination retry | CS course list | retrieve→generate→retry | ✅ PASS |
| 5 | Policy question | CGPA probation | retrieve→grade→generate | ✅ PASS |
