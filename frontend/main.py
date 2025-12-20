import gradio as gr
import sys
import os

# Add the parent directory to the system path to allow for imports from the 'agents' module
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from agents.precedent_searcher.runner import PrecedentSearchState, PrecedentSearchRunner

# Dummy data for dropdowns
jurisdiction_choices = ["Federal", "State A", "State B"]
date_range_choices = ["Last Year", "Last 5 Years", "All Time"]
area_of_law_choices = ["Tort Law", "Contract Law", "Criminal Law"]
court_level_choices = ["Supreme Court", "Appellate Court", "District Court"]

def search_precedents(user_input):
    """
    This function is called when the user clicks the 'Analyze & Search' button.
    It runs the precedent search agent and returns the results.
    """
    if not user_input:
        return "Please enter a case description.", "No results yet."

    # 1. Create a state object
    state = PrecedentSearchState(user_input)

    # 2. Create a runner and execute the search
    runner = PrecedentSearchRunner(state)
    final_memo = runner.run_full_search()

    # For now, we'll just return the raw output.
    # In a real application, you would parse this and format it nicely.
    extracted_facts = state.structured_facts if state.structured_facts else "Could not extract facts."
    suggested_precedents = final_memo if final_memo else "Could not find precedents."

    return extracted_facts, suggested_precedents

with gr.Blocks(title="Precedent Copilot") as demo:
    with gr.Row():
        # --- Sidebar ---
        with gr.Column(scale=1, min_width=200):
            gr.Markdown("# Precedent Copilot\n*Legal Assistant v2.0*")
            gr.Button("New Search", variant="primary")
            gr.Button("History")
            gr.Button("Saved Cases")
            gr.Button("Analytics")
            gr.Button("Settings")

        # --- Main Content ---
        with gr.Column(scale=4):
            # Header
            with gr.Row():
                gr.Markdown("## Case Analysis Dashboard")
                gr.Textbox(placeholder="Global search...", show_label=False, scale=1)
                gr.Button("Help & Support")
                gr.Markdown("👤") # Avatar placeholder

            # New Inquiry
            gr.Markdown("## New Inquiry\nInput testimony or upload legal briefs to find relevant precedents.")
            with gr.Group():
                inquiry_textbox = gr.Textbox(lines=7, placeholder="Paste testimony transcript, judge's notes, or describe the case facts here...", show_label=False)
                with gr.Row():
                    gr.Button("Record")
                    gr.Button("Upload File")
                    analyze_button = gr.Button("Analyze & Search", variant="primary")

            gr.Label("Analysis Ready | Waiting for input...")

            # Filters
            gr.Markdown("---")
            with gr.Row():
                gr.Markdown("### Filters:")
                gr.Dropdown(jurisdiction_choices, label="Jurisdiction")
                gr.Dropdown(date_range_choices, label="Date Range")
                gr.Dropdown(area_of_law_choices, label="Area of Law")
                gr.Dropdown(court_level_choices, label="Court Level")
                gr.Button("Reset All")

            # Results
            with gr.Row():
                # --- Extracted Facts Column ---
                with gr.Column():
                    gr.Markdown("### Extracted Facts")
                    extracted_facts_output = gr.Markdown("...")

                # --- Suggested Precedents Column ---
                with gr.Column():
                    gr.Markdown("### Suggested Precedents")
                    suggested_precedents_output = gr.Markdown("...")

    # Wire up the button to the search function
    analyze_button.click(
        fn=search_precedents,
        inputs=inquiry_textbox,
        outputs=[extracted_facts_output, suggested_precedents_output]
    )

if __name__ == "__main__":
    demo.launch()
