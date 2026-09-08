from functions import getSummary
import gradio as gr
from typing import Optional, Tuple
from PIL import Image


# **************************************
def greet(URL: str, language: str, OutputLength: str, sentiment: str) -> Tuple[str, str, Optional[Image.Image]]:
    """
    Gradio callback that maps UI selections to a getSummary call and runs it.

    URL: The EksiSozluk page URL to summarize.
    language: Output language, either "Turkish" or "English".
    OutputLength: Desired summary length, one of "short", "normal", or "long".
    sentiment: Whether to run sentiment analysis, either "on" or "off".

    RETURN: A tuple of (summary string, sentiment result string or "--" if
    sentiment analysis was skipped, pie chart Image or None if skipped).
    """
    result=""
    if language=="Turkish":
        if(OutputLength=="short"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=128, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=128, sentiment=True)
        elif(OutputLength=="normal"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=256, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=256, sentiment=True)
        elif(OutputLength=="long"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=1024, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="Turkish", tokens_create=1024, sentiment=True)
    
    elif language=="English":
        if(OutputLength=="short"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=128, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=128, sentiment=True)
        elif(OutputLength=="normal"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=256, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=256, sentiment=True)
        elif(OutputLength=="long"):
            if(sentiment=='off'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=512, sentiment=False)
            elif(sentiment=='on'):
                result, analysis, image = getSummary(url_main=URL, lang="English", tokens_create=512, sentiment=True)

    return result, analysis, image

if __name__ == "__main__": 
    demo = gr.Interface(
    fn=greet,
    inputs=[ "text", gr.Radio(["Turkish", "English"]), gr.Radio(["short", "normal", "long"]),  gr.Radio(["on", "off"])],
    outputs=[gr.Textbox(label="Summary Generated"), gr.Textbox(label="Sentiment Analysis Results"), gr.Image(type="pil", label="Sentiment Analysis Pie Chart")],
    title="EksiSUMM",
    description="Don't have time for reading all the entries in [EksiSozluk](http://eksisozluk.com/)? Then, you are at the right place!",
    article="Created by: [Onat Kaya](https://github.com/onatkaya)"
)

    demo.launch(share=False)
