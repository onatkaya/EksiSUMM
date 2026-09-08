# EksiSUMM 💧

## Description 🧠
**Don't have time for reading all the entries in [Eksi Sozluk](http://eksisozluk.com/)? Then, you are at the right place!**

Ekşi Sözlük is one of Turkey's most popular online forums, where users can create topic-specific _titles_ and contribute via posts called _entries_. These titles can contain multiple pages of content (dozens, even hundreds of pages sometimes), making it time-consuming to read through.

This project is a smart **summarization** 📝 and **sentiment analysis** 📊 tool that makes the reading experience smoother — powered entirely by **local, open-source AI models**, no paid API required. 🦙

## ✨ Highlights

- 🕸️ **Custom web scraper** — pulls every entry from a title, whether it spans 1 page or 100.
- 🤖 **Runs on open-source LLMs via [Ollama](https://ollama.com/)** — everything runs locally on your own machine, nothing sent to a paid API.
- 💬 **AI-generated Turkish summaries** of long, sprawling forum discussions.
- 😊😐☹️ **Sentiment analysis**, powered by a fine-tuned Turkish BERT model, with a visual pie-chart breakdown.
- 🖥️ **Simple web interface**, built with Gradio — no technical know-how needed to use it.

## Installation 🔧

```bash
git clone https://github.com/onatkaya/EksiSUMM.git

mkdir EksiSUMM
cd EksiSUMM

# create virtual environment
conda create -n eksi-venv python=3.10.0
conda activate eksi-venv

# install dependencies
pip install -r requirements.txt
```

## Usage 🔎
Before usage, make sure [Ollama](https://ollama.com/) is installed and running locally, and pull the model used by the app (defaults to `qwen2.5:3b`):

```bash
ollama pull qwen2.5:3b
```

You can point the app at a different local model via the `OLLAMA_MODEL` environment variable, and adjust how much context is given to the model (larger titles need more) via `OLLAMA_NUM_CTX` (defaults to `16384`).

To use the application, just run:

```bash
python app.py
```
Afterwards, you should be directed to a `localhost` address, where you can play with EksiSUMM.

## How It Works? ⚙️

- 🔗 The user provides a URL pointing to a specific topic on Ekşi Sözlük.
  - The URL must be in the specific format: https://eksisozluk.com/title-name-here--title_id
  - It should not have any text elsewhere (_e.g._ after the URL of the title specified).
  - **Example**: [https://eksisozluk.com/seoul-national-university--4258420](https://eksisozluk.com/seoul-national-university--4258420)
  - **Example**: [https://eksisozluk.com/osaka--227690](https://eksisozluk.com/osaka--227690)

- 🕷️ A custom-built scraper (using BeautifulSoup) collects all entries from every available page under that topic — whether it contains 1 page or 100.

- 🧠 The collected entries are then passed to a local, open-source model served via [Ollama](https://ollama.com/) (default: `qwen2.5:3b`) for summarization.

- 📈 **Optional:** Users can enable **sentiment analysis**, powered by a fine-tuned BERT model called [TurkishBERTweet](https://huggingface.co/VRLLab/TurkishBERTweet). It works by classifying each entry as `positive`, `neutral` or `negative`. The results are displayed both numerically and visually (pie chart) 🥧.

### Tech Stack 📚

* Python (`version>=3.10`)
* BeautifulSoup (for custom scraper building)
* Transformers & PEFT (Hugging Face)
* Hugging Face Spaces
* Ollama (local open-source LLMs, e.g. Qwen2.5)
* Gradio
* Matplotlib


## Limitations & Disclaimer ⚠️

* Summary quality depends on the local model you run — smaller/quantized models may degrade on very long titles; tune `OLLAMA_NUM_CTX` and pick a model that fits your hardware.
* The application EksiSUMM and its creator _(yours truly)_ is not responsible for the factual accuracy of the summary provided. This application mainly focuses on summarizing the (mostly subjective) entries written by users online.

## Contact

For questions and inquiries, you could contact via my email `mronatkaya@gmail.com` or [LinkedIn](https://www.linkedin.com/in/onat-kaya2/)

## Credits

If you use this code for your work, please cite this GitHub repository.

```
@software{onatkaya_EksiSUMM,
  author       = {onatkaya},
  title        = {onatkaya/EksiSUMM},
  month        = may,
  year         = 2025,
  url          = {https://github.com/onatkaya/EksiSUMM}
}
```

## License
This project is licensed under the MIT License.
