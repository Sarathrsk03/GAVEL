import gradio as gr

# Dummy data for dropdowns
jurisdiction_choices = ["Federal", "State A", "State B"]
date_range_choices = ["Last Year", "Last 5 Years", "All Time"]
area_of_law_choices = ["Tort Law", "Contract Law", "Criminal Law"]
court_level_choices = ["Supreme Court", "Appellate Court", "District Court"]

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
                gr.Textbox(lines=7, placeholder="Paste testimony transcript, judge's notes, or describe the case facts here...", show_label=False)
                with gr.Row():
                    gr.Button("Record")
                    gr.Button("Upload File")
                    gr.Button("Analyze & Search", variant="primary")

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
                    with gr.Group():
                        gr.Markdown("**HIGH RELEVANCE**")
                        gr.Markdown('"The defendant was operating the vehicle at 45mph in a 30mph zone during heavy rain."')
                        gr.Markdown("_Source: Witness Testimony (Line 14)_")

                    with gr.Group():
                        gr.Markdown("**MEDIUM RELEVANCE**")
                        gr.Markdown('"Visual obstruction claimed due to parked delivery truck."')
                        gr.Markdown("_Source: Defendant Statement_")

                    with gr.Group():
                        gr.Markdown("**CONTEXT**")
                        gr.Markdown('"Incident occurred at approximately 11:30 PM."')
                        gr.Markdown("_Source: Defendant Statement_")

                # --- Suggested Precedents Column ---
                with gr.Column():
                    gr.Markdown("### Suggested Precedents")
                    with gr.Group():
                        with gr.Row():
                            with gr.Column(scale=3):
                                gr.Markdown("#### Smith v. Jones Transport\n_2018 NY Slip Op 04512 [2d Dept]_")
                            with gr.Column(scale=1):
                                gr.Markdown("## 98%\nMatch Score")
                        gr.Markdown("Establishes liability in similar weather conditions where the driver failed to adjust speed despite being within the technical speed limit. The court held that \"reasonable prudence\" dictates speed reduction in heavy rain.")
                        with gr.Row():
                            gr.Button("#Negligence")
                            gr.Button("#TrafficLaw")
                            gr.Button("#AdverseWeather")
                        with gr.Row():
                           gr.Markdown("Supreme Court")
                           gr.Markdown("Oct 12, 2018")
                           gr.Markdown("[Read Full Case →](http://example.com)")

                    with gr.Group():
                        with gr.Row():
                            with gr.Column(scale=3):
                                gr.Markdown("#### City of NY v. Doe\n_2021 NY Slip Op 11201 [1st Dept]_")
                            with gr.Column(scale=1):
                                gr.Markdown("## 85%\nMatch Score")
                        gr.Markdown("Addressed the \"Visual Obstruction\" defense. The court ruled that a parked vehicle...")

if __name__ == "__main__":
    demo.launch()
