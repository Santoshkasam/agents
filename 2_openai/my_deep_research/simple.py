import gradio as gr
from dotenv import load_dotenv
from research_manager import research_manager

load_dotenv(override=True)
research_manager = research_manager()
async def run(query: str):
    async for status_update in research_manager.run(query=query):
        yield status_update

with gr.Blocks() as ui:
    query_textbox = gr.Textbox(label="What topic would you like to research?")
    run_button    = gr.Button("Run", variant="primary")
    report        = gr.Markdown(label="Report")

    run_button.click(run, inputs=query_textbox, outputs=report)
    query_textbox.submit(run, inputs=query_textbox, outputs=report)

ui.launch(theme=gr.themes.Default(primary_hue="sky"))