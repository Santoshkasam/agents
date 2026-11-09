import gradio as gr
from dotenv import load_dotenv
from research_manager import research_manager
from styles import CSS, JS, EXAMPLES, HEADER_HTML

load_dotenv(override=True)


async def run(query: str, followup_questions: str, followup_answer: str):
    async for status_update in research_manager().run(
        query, followup_questions, followup_answer
    ):
        yield status_update


async def prepare_followups(query: str):
    questions = await research_manager().generate_followup_questions(query)
    return questions, questions, query, gr.update(visible=True), "", ""


with gr.Blocks(title="Deep Research") as ui:
    gr.HTML(HEADER_HTML)

    with gr.Row(elem_classes="dr-query-row"):
        query_textbox = gr.Textbox(
            placeholder="Type a research question...",
            show_label=False,
            container=False,
            autofocus=True,
            elem_id="dr-query",
            scale=5,
        )
        run_button = gr.Button("Investigate", variant="primary", elem_id="dr-run", scale=1)

    gr.HTML('<div class="dr-examples-label">Try one</div>')
    gr.Examples(examples=EXAMPLES, inputs=query_textbox, elem_id="dr-examples")

    followup_questions_state = gr.State("")
    prepared_query_state = gr.State("")
    with gr.Column(visible=False, elem_id="dr-followups") as followup_panel:
        followup_prompt = gr.Markdown()
        followup_answer = gr.Textbox(
            label="Your answers",
            placeholder="Answer the questions above, in order...",
            lines=4,
        )
        continue_button = gr.Button(
            "Continue research", variant="primary", elem_id="dr-continue"
        )

    report = gr.Markdown(elem_id="dr-report")

    prepare_outputs = [
        followup_prompt,
        followup_questions_state,
        prepared_query_state,
        followup_panel,
        followup_answer,
        report,
    ]
    run_button.click(prepare_followups, inputs=query_textbox, outputs=prepare_outputs)
    query_textbox.submit(
        prepare_followups, inputs=query_textbox, outputs=prepare_outputs
    )

    continue_event = continue_button.click(
        run,
        inputs=[prepared_query_state, followup_questions_state, followup_answer],
        outputs=report,
    )
    continue_event.then(
        lambda: gr.update(visible=False),
        outputs=followup_panel,
    )


if __name__ == "__main__":
    ui.launch(css=CSS, js=JS, theme=gr.themes.Base())
