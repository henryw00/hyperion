import gradio as gr
import pandas as pd
from search import find_similar_claims

# Helper function to generate the HTML cards based on a slice of the dataframe
def generate_html(matches_df, search_time, total_records):
    # Notice: Emoji removed from the header here as well
    output_html = f"<div style='margin-bottom: 15px; color: #4b5563; font-size: 0.9em;'>Searched {total_records} historical claims in <b>{search_time:.4f} seconds</b>. Showing top {len(matches_df)}.</div>"
    
    output_html += "<div style='display: flex; flex-direction: column; gap: 15px;'>"
    
    for _, row in matches_df.iterrows():
        amount = f"${row['settlement_amount']:,.0f}" if pd.notna(row['settlement_amount']) else f"${row['reserve_amount']:,.0f} (Reserved)"
        
        output_html += f"""
        <div style='border: 1px solid #374151; padding: 20px; border-radius: 12px; background-color: #1f2937; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);'>
            <h3 style='margin-top: 0; color: #f9fafb; font-size: 1.25em;'>
                [{row['id']}] {row['loss_type']} 
                <span style='font-size: 0.8em; color: #a1a1aa; font-weight: normal; margin-left: 10px;'>
                    ({row['Similarity_Score']:.2f} Semantic Match)
                </span>
            </h3>
            
            <div style='display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 12px; margin-bottom: 15px; font-size: 0.95em; color: #d1d5db;'>
                <div>
                    <b style='color: #e5e7eb; font-weight: 600;'>Outcome:</b> 
                    <span style='margin-left: 5px;'>{row['outcome']}</span>
                </div>
                <div>
                    <b style='color: #e5e7eb; font-weight: 600;'>Jurisdiction:</b> 
                    <span style='margin-left: 5px;'>{row['jurisdiction']}</span>
                </div>
                <div>
                    <b style='color: #e5e7eb; font-weight: 600;'>Financials:</b> 
                    <span style='margin-left: 5px;'>{amount}</span>
                </div>
                
                <div style='grid-column: span 3;'>
                    <b style='color: #e5e7eb; font-weight: 600;'>Key Factors:</b> 
                    <span style='margin-left: 5px;'>{', '.join(row['key_factors'])}</span>
                </div>
            </div>
            
            <p style='margin-bottom: 0; color: #d1d5db; font-style: italic; line-height: 1.5; background-color: rgba(255,255,255,0.03); padding: 10px; border-radius: 6px;'>
                "{row['description']}"
            </p>
        </div>
        """
    output_html += "</div>"
    return output_html

# Action for the initial search button
def initial_search(claim_text):
    if not claim_text.strip():
        return "Please enter a claim description.", None, 0, 0.0, gr.update(visible=False)
    
    # Get the full sorted dataset from the backend
    all_matches, search_time = find_similar_claims(claim_text)
    total_records = len(all_matches)
    
    # Start by showing 3 records
    display_count = 3
    matches_slice = all_matches.head(display_count)
    
    html = generate_html(matches_slice, search_time, total_records)
    
    # Decide if the Show More button should be visible
    show_button = display_count < total_records
    
    return html, all_matches, display_count, search_time, gr.update(visible=show_button)

# Action for the Show More button
def load_more(all_matches, current_count, search_time):
    # Increase the display count by 3
    new_count = current_count + 3
    total_records = len(all_matches)
    
    # Prevent going out of bounds
    if new_count > total_records:
        new_count = total_records
        
    matches_slice = all_matches.head(new_count)
    html = generate_html(matches_slice, search_time, total_records)
    
    # Hide button if we reached the end of the dataset
    show_button = new_count < total_records
    
    return html, new_count, gr.update(visible=show_button)

custom_css = """
@import url('https://fonts.googleapis.com/css2?family=Roboto:ital,wght@0,400;0,500;0,700;1,400&display=swap');

body, * {
    font-family: 'Google Sans', 'Roboto', 'Helvetica Neue', Arial, sans-serif !important;
}
body {
    background-color: #f9fafb !important;
}
button.primary, button.secondary {
    background-color: #1f2937 !important;
    border-color: #1f2937 !important;
    color: #f9fafb !important;
}
button.primary:hover, button.secondary:hover {
    background-color: #374151 !important;
    border-color: #374151 !important;
}
"""

with gr.Blocks(css=custom_css) as demo:
    gr.Markdown(
        """
        # Hyperion: Claims Similarity Prototype
        Enter an unstructured FNOL (First Notice of Loss) description below to surface relevant historical precedents from our knowledge base of over 1,000 historical claims.
        """
    )
    
    # State variables to hold data between button clicks
    matches_state = gr.State()
    count_state = gr.State(0)
    time_state = gr.State(0.0)
    
    with gr.Row():
        with gr.Column(scale=1):
            claim_input = gr.Textbox(
                lines=8, 
                label="New Claim (FNOL) Description", 
                placeholder="e.g., Water damage to retail store inventory after pipe burst. Tenant is claiming $180K in damaged goods. Landlord says tenant failed to report leak earlier."
            )
            search_btn = gr.Button("Find Contextual Precedents", variant="primary")
        
        with gr.Column(scale=2):
            results_output = gr.HTML(label="Historical Matches")
            # Secondary button for pagination, hidden by default
            show_more_btn = gr.Button("Show More Cases", variant="secondary", visible=False)
            
    # Wire up the events
    search_btn.click(
        fn=initial_search, 
        inputs=[claim_input], 
        outputs=[results_output, matches_state, count_state, time_state, show_more_btn]
    )
    
    show_more_btn.click(
        fn=load_more,
        inputs=[matches_state, count_state, time_state],
        outputs=[results_output, count_state, show_more_btn]
    )

if __name__ == "__main__":
    demo.launch()