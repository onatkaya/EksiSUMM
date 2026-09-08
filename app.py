from functions import getSummary
import gradio as gr
from typing import Literal
from PIL import Image


# **************************************
def greet(URL: str, sentiment: Literal["on", "off"]) -> tuple[str, str, Image.Image | None]:
    """
    Gradio callback that maps UI selections to a getSummary call and runs it.

    URL: The EksiSozluk page URL to summarize.
    sentiment: Whether to run sentiment analysis, either "on" or "off".

    RETURN: A tuple of (summary string, sentiment result string or "--" if
    sentiment analysis was skipped, pie chart Image or None if skipped).
    """
    result=""

    if(sentiment=='off'):
        result, analysis, image = getSummary(url_main=URL, tokens_create=750, sentiment=False)
    elif(sentiment=='on'):
        result, analysis, image = getSummary(url_main=URL, tokens_create=750, sentiment=True)
    
    return result, analysis, image

if __name__ == "__main__": 
    demo = gr.Interface(
    fn=greet,
    inputs=[ "text",  gr.Radio(["on", "off"])],
    outputs=[gr.Textbox(label="Summary Generated"), gr.Textbox(label="Sentiment Analysis Results"), gr.Image(type="pil", label="Sentiment Analysis Pie Chart")],
    title="EksiSUMM",
    description="Don't have time for reading all the entries in [EksiSozluk](http://eksisozluk.com/)? Then, you are at the right place!",
    article="Created by: [Onat Kaya](https://github.com/onatkaya)"
)

    demo.launch(share=False)
