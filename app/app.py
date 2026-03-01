import json
import time
import pandas as pd
import gradio as gr
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity

# --- Backend Search Logic ---

print("Loading AI model (all-MiniLM-L6-v2)...")
model = SentenceTransformer('all-MiniLM-L6-v2')

def load_data(filepath):
    with open(filepath, 'r') as file:
        raw_data = json.load(file)
    df = pd.DataFrame(raw_data['claims'])
    df['searchable_text'] = df['description'] + " Key factors: " + df['key_factors'].apply(lambda x: ", ".join(x))
    return df

print("Loading large dataset...")
df = load_data('large_claims_data.json')

print(f"Embedding {len(df)} historical claims... (This will take a few minutes)")
historical_embeddings = model.encode(df['searchable_text'].tolist(), show_progress_bar=True)
print("Ready!")

def get_unique_jurisdictions():
    return sorted(df['jurisdiction'].unique().tolist())

def get_unique_policy_types():
    return sorted(df['policy_type'].unique().tolist())

def find_similar_claims(new_claim_text, jurisdiction_filter=[], policy_filter=[]):
    start_time = time.time() 
    query_embedding = model.encode([new_claim_text])
    similarities = cosine_similarity(query_embedding, historical_embeddings)[0]
    
    results = df.copy()
    results['Similarity_Score'] = similarities
    
    if jurisdiction_filter:
        results = results[results['jurisdiction'].isin(jurisdiction_filter)]
    if policy_filter:
        results = results[results['policy_type'].isin(policy_filter)]
        
    results = results.sort_values(by='Similarity_Score', ascending=False)
    end_time = time.time() 
    return results, end_time - start_time

# --- LLM Synthesis Logic ---

def generate_synthesis(fnol_text, selected_case_strings, all_matches_df):
    if not selected_case_strings:
        return "Please select at least one case to generate a plan."
    
    selected_ids = [s.split(" - ")[0] for s in selected_case_strings]
    selected_df = all_matches_df[all_matches_df['id'].isin(selected_ids)]
    
    amounts = []
    for _, row in selected_df.iterrows():
        if pd.notna(row['settlement_amount']):
            amounts.append(row['settlement_amount'])
        elif pd.notna(row['reserve_amount']):
            amounts.append(row['reserve_amount'])
            
    avg_amount = sum(amounts) / len(amounts) if amounts else 0
    min_amount = min(amounts) if amounts else 0
    max_amount = max(amounts) if amounts else 0
    
    factors = set()
    for f_list in selected_df['key_factors']:
        factors.update(f_list)
    top_factors = list(factors)[:3]
    
    report = f"""
### Opt-In Action Plan

**The Precedent**
The selected historical claims share critical semantic overlap with the new First Notice of Loss. Specifically, the recurring key factors across these cases involve **{', '.join(top_factors)}**. In previous instances, these specific elements heavily influenced the liability determination and final settlement trajectory.

**Financial Baseline**
Based on the {len(selected_df)} selected precedents, the financial exposure is bounded as follows:
* **Minimum Exposure:** ${min_amount:,.0f}
* **Maximum Exposure:** ${max_amount:,.0f}
* **Historical Average:** ${avg_amount:,.0f}

**Recommended Next Steps**
1. **Immediate Fact-Finding:** Secure any documentation related to {top_factors[0]} immediately, as missing evidence in historical cases led to the higher end of the financial baseline.
2. **Reserve Alignment:** Consider setting the initial reserve near the historical average of **${avg_amount:,.0f}** pending the discovery phase.
3. **Jurisdictional Review:** Verify local statutes regarding comparative negligence for this specific loss type.
"""
    return report

# --- UI Logic ---

def generate_html(matches_df, search_time, total_records):
    # Notice how much cleaner this is! No inline styles, just CSS classes.
    output_html = f"<div class='results-header'>Searched {total_records} historical claims in <b>{search_time:.4f} seconds</b>. Showing top {len(matches_df)}.</div>"
    output_html += "<div style='display: flex; flex-direction: column; gap: 15px;'>"
    
    for _, row in matches_df.iterrows():
        amount = f"${row['settlement_amount']:,.0f}" if pd.notna(row['settlement_amount']) else f"${row['reserve_amount']:,.0f} (Reserved)"
        
        output_html += f"""
        <div class='claim-card'>
            <h3 class='claim-title'>
                [{row['id']}] {row['loss_type']} 
                <span class='claim-title-match'>({row['Similarity_Score']:.2f} Semantic Match)</span>
            </h3>
            <div class='claim-meta'>
                <div><b>Outcome:</b><span>{row['outcome']}</span></div>
                <div><b>Jurisdiction:</b><span>{row['jurisdiction']}</span></div>
                <div><b>Financials:</b><span>{amount}</span></div>
                <div style='grid-column: span 3;'><b>Key Factors:</b><span>{', '.join(row['key_factors'])}</span></div>
            </div>
            <p class='claim-desc'>"{row['description']}"</p>
        </div>
        """
    output_html += "</div>"
    return output_html

def toggle_synthesis_btn(selected_cases):
    if selected_cases and len(selected_cases) > 0:
        return gr.update(visible=True)
    return gr.update(visible=False)

def initial_search(claim_text, jurisdiction, policy):
    if not claim_text.strip():
        return "Please enter a claim description.", None, 0, 0.0, gr.update(visible=False), gr.update(choices=[]), gr.update(visible=False), "", gr.update(visible=False)
    
    all_matches, search_time = find_similar_claims(claim_text, jurisdiction_filter=jurisdiction, policy_filter=policy)
    total_records = len(all_matches)
    
    display_count = 3
    matches_slice = all_matches.head(display_count)
    
    html = generate_html(matches_slice, search_time, total_records)
    show_button = display_count < total_records
    
    checkbox_choices = [f"{row['id']} - {row['loss_type']}" for _, row in matches_slice.iterrows()]
    
    return html, all_matches, display_count, search_time, gr.update(visible=show_button), gr.update(choices=checkbox_choices, value=[]), gr.update(visible=True, open=False), "", gr.update(visible=False)

def load_more(all_matches, current_count, search_time):
    new_count = current_count + 3
    total_records = len(all_matches)
    
    if new_count > total_records:
        new_count = total_records
        
    matches_slice = all_matches.head(new_count)
    html = generate_html(matches_slice, search_time, total_records)
    show_button = new_count < total_records
    
    checkbox_choices = [f"{row['id']} - {row['loss_type']}" for _, row in matches_slice.iterrows()]
    
    return html, new_count, gr.update(visible=show_button), gr.update(choices=checkbox_choices)

# The new dual-theme CSS mapping
custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,500;0,700;1,400&display=swap');

body, * { font-family: 'Google Sans', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important; }

/* Base App Buttons (Automatically adapt but force strict edges) */
button.primary { background-color: #1f2937 !important; border-color: #1f2937 !important; color: #f9fafb !important; }
button.primary:hover { background-color: #374151 !important; border-color: #374151 !important; }

/* -------------------------------------
   Light Mode (Base Default) 
   ------------------------------------- */
.claim-card {
    border: 1px solid #9ca3af;
    padding: 20px;
    border-radius: 12px;
    background-color: #ffffff;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
}
.claim-title {
    margin-top: 0;
    color: #111827;
    font-size: 1.25em;
}
.claim-title-match {
    font-size: 0.8em;
    color: #6b7280;
    font-weight: normal;
    margin-left: 10px;
}
.claim-meta {
    display: grid;
    grid-template-columns: 1fr 1fr 1fr;
    gap: 12px;
    margin-bottom: 15px;
    font-size: 0.95em;
    color: #374151;
}
.claim-meta b {
    color: #111827;
    font-weight: 600;
}
.claim-meta span { margin-left: 5px; }

.claim-desc {
    margin-bottom: 0;
    color: #4b5563;
    font-style: italic;
    line-height: 1.5;
    background-color: #f3f4f6;
    padding: 10px;
    border-radius: 6px;
}
.results-header {
    margin-bottom: 15px;
    color: #4b5563;
    font-size: 0.9em;
}

/* -------------------------------------
   Dark Mode Overrides
   ------------------------------------- */
.dark .claim-card {
    border-color: #374151;
    background-color: #1f2937;
}
.dark .claim-title { color: #f9fafb; }
.dark .claim-title-match { color: #a1a1aa; }
.dark .claim-meta { color: #d1d5db; }
.dark .claim-meta b { color: #e5e7eb; }
.dark .claim-desc {
    color: #d1d5db;
    background-color: rgba(255,255,255,0.03);
}
.dark .results-header { color: #9ca3af; }
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown("# Hyperion: Claims Similarity Prototype\nEnter an unstructured FNOL (First Notice of Loss) description below to surface relevant historical precedents from our knowledge base of over 50,000 historical claims.")
    
    matches_state = gr.State()
    count_state = gr.State(0)
    time_state = gr.State(0.0)
    
    with gr.Row():
        with gr.Column(scale=1):
            claim_input = gr.Textbox(lines=8, label="New Claim (FNOL) Description", placeholder="e.g., Water damage to retail store inventory after pipe burst.")
            with gr.Row():
                jurisdiction_dropdown = gr.Dropdown(choices=get_unique_jurisdictions(), value=[], multiselect=True, label="Jurisdiction (Leave blank for all)")
                policy_dropdown = gr.Dropdown(choices=get_unique_policy_types(), value=[], multiselect=True, label="Policy Type (Leave blank for all)")
            search_btn = gr.Button("Find Contextual Precedents", variant="primary")
        
        with gr.Column(scale=2):
            with gr.Accordion("Advanced Synthesis Panel", open=False, visible=False) as synthesis_accordion:
                gr.Markdown("Select specific cases from the results below to build a custom investigation plan.")
                selected_cases = gr.CheckboxGroup(label="Selected Cases", choices=[])
                synthesis_btn = gr.Button("Generate Investigation Plan", variant="primary", visible=False)
                synthesis_output = gr.Markdown("")

            results_output = gr.HTML(label="Historical Matches")
            show_more_btn = gr.Button("Show More Cases", variant="secondary", visible=False)
            
    search_btn.click(
        fn=initial_search, 
        inputs=[claim_input, jurisdiction_dropdown, policy_dropdown], 
        outputs=[results_output, matches_state, count_state, time_state, show_more_btn, selected_cases, synthesis_accordion, synthesis_output, synthesis_btn]
    )
    
    show_more_btn.click(
        fn=load_more,
        inputs=[matches_state, count_state, time_state],
        outputs=[results_output, count_state, show_more_btn, selected_cases]
    )
    
    selected_cases.change(
        fn=toggle_synthesis_btn,
        inputs=[selected_cases],
        outputs=[synthesis_btn]
    )
    
    synthesis_btn.click(
        fn=generate_synthesis,
        inputs=[claim_input, selected_cases, matches_state],
        outputs=[synthesis_output]
    )

if __name__ == "__main__":
    demo.launch()