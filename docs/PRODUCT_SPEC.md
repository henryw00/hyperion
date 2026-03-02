# Product Specification: Hyperion MVP

## 1. Problem Statement
The primary bottleneck in insurance claims adjustment is information retrieval. When evaluating a new First Notice of Loss (FNOL), adjusters often look to historical precedent to establish a financial baseline and identify key investigative factors. However, extracting that context using legacy systems is a massively time-consuming manual process due to inefficient keyword matching searches. 

Adjusters waste hours guessing exact keyword combinations (e.g., trying "tenant fell," "customer slipped," and "slip and fall" just to find the same incident type) and skimming thousands of irrelevant files that share vocabulary but lack situational context. This administrative friction severely limits the number of claims an adjuster can process per day, increasing cycle times and operational costs for the carrier.

## 2. Target User & Context
**Primary User: The Claims Adjuster**
* **Context:** Carries a high volume of open claims and operates in a fast-paced, time-poor environment. 
* **Motivation:** Needs to process new claims rapidly to prevent backlog. They want to find relevant historical context instantly, establish a baseline, and initiate the investigation without breaking their workflow.
* **Pain Point:** Frustrated by slow, rigid legacy software that turns a five-minute task into a two-hour research project.

## 3. Proposed Solution
Hyperion is a semantic search engine and synthesis tool designed strictly to accelerate the claims workflow. The MVP focuses entirely on reducing the time-to-insight. By giving Hyperion a FNOL description, it will be able to find the closest semantically matching claims and generate an investigation plan based on said matches. 

**Core Capabilities:**
* **Semantic Search:** Replaces keyword guessing with Natural Language Processing. Adjusters paste unstructured FNOL text, and the system uses vector embeddings to instantly surface historical files with matching situational context.
* **Metadata Filtering:** Multi-select metadata filters (Jurisdiction and Policy Type) ensure the adjuster spends zero time reading claims from structurally irrelevant states or lines of business.
* **Automated Synthesis:** Instead of manually reading matches to calculate averages, the adjuster selects the most relevant precedents, and Hyperion instantly generates an aggregate financial baseline (Min/Max/Mean) and extracts overlapping key factors.


## 4. Key Design Decisions & Tradeoffs
* **Tradeoff 1: In-Memory Pandas vs. Dedicated Vector Database**
  * **Decision:** Used in-memory Pandas and Scikit-Learn cosine similarity instead of a dedicated Vector DB (like FAISS or Pinecone).
  * **Why:** To ensure the MVP runs entirely locally with zero external dependencies or complex containerization required for setup. Traded extreme scaling (>100,000 records) for ease of deployment and immediate offline testing. 
* **Tradeoff 2: Procedural Synthesis vs. Live LLM API**
  * **Decision:** Built a procedural extraction engine to generate the investigation plan and financial baselines rather than calling a live LLM (like GPT-4).
  * **Why:** To guarantee sub-second execution speed, ensure 100% deterministic math for the financial baselines, and eliminate API key requirements for the prototype. Traded natural-language fluidity for absolute speed and reliability.
* **Tradeoff 3: Opt-In Synthesis vs. Auto-Summarization**
  * **Decision:** The system requires the adjuster to manually check boxes next to relevant cases before generating a synthesis, rather than automatically summarizing the top 3 results.
  * **Why:** To keep the human expert in the loop. If the search returns two perfect matches and one false positive, an automated summary would blend the false positive into the baseline. The adjuster gets the final say for which cases actually matter. 

## 5. Success Metrics
To prove Hyperion accelerates adjuster workfloww, the following metrics should be tracked during the pilot phase:

* **Primary Metric: Time to First Actionable Insight**
  * *Definition:* The time elapsed between a user pasting an FNOL and generating a synthesis report.
  * *Target:* <1 minute, this would indicate users are able to quickly find relevant information.
* **Secondary Metric: Search Refinement Rate**
  * *Definition:* The average number of subsequent search queries executed per session.
  * *Target:* <2 queries. Using a single query indicates the semantic search is surfacing the correct context on the first attempt, eliminating keyword guessing.
* **Engagement Metric: Synthesis Adoption Rate**
  * *Definition:* The percentage of total searches where the user clicks "Generate Investigation Plan."
  * *Target:* > 60%. High adoption proves the data extracted is trusted and saves manual labor.

## 6. Future Development Roadmap (v2.0+)
To transition Hyperion from a high-performance local MVP to an enterprise-grade cloud application:

* **Vector Indexing Infrastructure:** Replace the in-memory array with a distributed vector database (e.g., Milvus or Pinecone) to support querying 10M+ enterprise records while maintaining sub-second latency. This will allow the system to scale to enterprise-size datasets.
* **Agentic AI Integration:** Introduce an optional LLM agent to summarize massive, 50-page claim files on demand, further reducing the adjuster's reading time. This requires an API key that I did not have access to, so a simpler prototype was built. An AI agent specialized in insurance claims would be able to summarize the key factors and financial baselines of a claim file in a matter of seconds.
* **One-Click System of Record Export:** Build API bridges to legacy claims management systems (e.g., Guidewire) allowing adjusters to push the generated financial baselines and key factors directly into the official file notes with a single click. Reduce manual labor. 
* **Model Accuracy Feedback Support:** Introduce a feedback loop to allow adjusters to rate the accuracy of the system's recommendations. This will allow the system to learn from its mistakes and improve over time.