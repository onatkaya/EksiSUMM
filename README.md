# EksiSUMM 💧
### Try it at [Hugging Face Spaces 🤗](https://huggingface.co/spaces/mronatkaya/eksiSUMM)!

## Description 🧠
**Don't have time for reading all the entries in [Eksi Sozluk](http://eksisozluk.com/)? Then, you are at the right place!**

Ekşi Sözlük is one of Turkey’s most popular online forums, where users can create topic-specific _titles_ and contribute via posts called _entries_. These titles can contain multiple pages of content (dozens, even hundreds of pages sometimes), making it time-consuming to read through.

This project is a smart **summarization** and **sentiment analysis** tool to make the reading experience smoother, using modern language models.

## Installation 🔧

```bash
git clone https://github.com/onatkaya/EksiSUMM.git

cd EksiSUMM
conda create -n eksi-venv python=3.10.0
conda activate eksi-venv

pip install -r requirements.txt
```

## Usage 🔎
Before usage, the user needs to introduce an OpenAI API key, to the system. For the summarizer based on LLM to work well.

To use the application, just run:

```bash
python app.py
```
Afterwards, you should be directed to a `localhost` address, where you can play with EksiSUMM.

## How It Works? ⚙️

TBD.

### Tech Stack 📚

* Python (version==3.10.0) 
* BeautifulSoup (for custom scraper building)
* Transformers (Hugging Face)
* Hugging Face Spaces
* OpenAI API (GPT-4o-mini)
* Gradio
* Matplotlib 
* `os` module

## To-Do List 🎯

- ✅ Push the application on Hugging Face Spaces 🤗
- ✅ Publish the repo on GitHub.
-  🎯 Improve flexibility on input URL provided.
-  🎯 Bigger and better and stronger LLMs?

## Limitations & Disclaimer ⚠️

* The sentiment analysis model might not perform well on very large input sizes. For this, only the most recent 200 entries are used when analyzing sentiment on Eksi Sozluk titles with 200+ entries.
* The application EksiSUMM and its creator _(yours truly)_ is not responsible for the factual accuracy of the summary provided. This application mainly focuses on summarizing the (mostly subjective) entries written by users online.

## License
This project is licensed under the MIT License.
