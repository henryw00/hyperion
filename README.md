Hyperion: AI-Powered Claims Similarity Engine
Overview
Hyperion is a specialized AI decision-support tool designed to accelerate and optimize the insurance claims adjustment process. When an adjuster receives a raw, unstructured First Notice of Loss (FNOL), Hyperion utilizes Natural Language Processing (NLP) and semantic vector search to instantly surface highly relevant historical claim precedents from a database of over 50,000 records.

By anchoring new claims against historical data, Hyperion reduces manual database querying, minimizes human error in reserve estimation, and standardizes claim outcomes across varying jurisdictions.

Core Features
Semantic Vector Search: Replaces rigid keyword matching with contextual understanding. Hyperion uses the all-MiniLM-L6-v2 sentence-transformer model to map unstructured FNOL descriptions into dense vector space, finding historical claims with similar underlying circumstances even if the vocabulary differs.

Dynamic Multi-Select Filtering: Employs efficient post-filtering logic via Pandas, allowing adjusters to narrow down semantic matches by specific combinations of Jurisdictions (e.g., CA, TX, NY) and Policy Types (e.g., Commercial Auto, General Liability).

Opt-In Investigation Synthesis: An advanced, interactive panel that allows adjusters to select specific historical matches to generate a custom investigation plan. The engine calculates the financial baseline (minimum, maximum, and average historical exposures) and extracts shared key factors to recommend immediate next steps.

High-Volume Capability: Engineered to process and embed 50,000+ records in memory with progress tracking, demonstrating robust local computational scaling.

Adaptive User Interface: Built with Gradio, featuring a custom CSS injection that provides a responsive, high-contrast experience supporting both Light and Dark system modes.

Local Installation and Setup Guide
Follow these steps to run the Hyperion application on your local machine.

Prerequisites
Python 3.8 or higher

Git

1. Clone the Repository
Open your terminal and clone the repository to your local machine:

git clone https://github.com/YOUR-USERNAME/hyperion.git

cd hyperion

2. Set Up the Virtual Environment
It is highly recommended to use a virtual environment to isolate the project dependencies.

For Windows:

python -m venv venv

.\venv\Scripts\activate

For macOS/Linux:

python3 -m venv venv

source venv/bin/activate

3. Install Dependencies
With the virtual environment active, install the required Python libraries.

pip install pandas gradio sentence-transformers scikit-learn

4. Generate the Synthetic Dataset
Hyperion requires a foundational dataset to run. Execute the data generation script to create a local JSON file containing 50,000 synthetic historical claims. This will create a file named large_claims_data.json in your root directory.

python generate_data.py

5. Launch the Application
Start the Hyperion server:

python app.py

Upon startup, the backend will load the dataset and compute the vector embeddings. A progress bar will display in the terminal. Once complete, the terminal will output a local URL (typically http://127.0.0.1:7860). Open this link in your web browser to interact with Hyperion.

Usage Workflow
Type or paste a claim description into the New Claim (FNOL) Description box.

(Optional) Apply filters using the Jurisdiction and Policy Type dropdowns.

Click Find Contextual Precedents.

Review the top matches. To load more, click Show More Cases.

To generate an action plan, expand the Advanced Synthesis Panel, select the checkboxes for the most relevant precedents, and click Generate Investigation Plan.