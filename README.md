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

- The user provides a URL pointing to a specific topic on Ekşi Sözlük.
  - The URL must be in the specific format: https://eksisozluk.com/title-name-here--title_id
  - It should not have any text elsewhere (_e.g._ after the title of the URL).
  - Example: [https://eksisozluk.com/seoul-national-university--4258420](https://eksisozluk.com/seoul-national-university--4258420)
  - Example: [https://eksisozluk.com/osaka--227690](https://eksisozluk.com/osaka--227690)

- A custom-built scraper (using BeautifulSoup) collects all entries from every available page under that topic — whether it contains 1 page or 100.

- The collected entries are then passed to OpenAI’s GPT-4o-mini for summarization. A carefully designed prompt ensures the summaries are informative and concise.

- **Users can customize:**

  - Summary Length: `short` (128 tokens), `normal` (256 tokens), or `long` (512 tokens)

  - Summary Language: Turkish or English

- **Optional:** Users can enable **sentiment analysis**, powered by a fine-tuned BERT model called [TurkishBERTweet](https://huggingface.co/VRLLab/TurkishBERTweet). It works by classifying each entry as `positive`, `neutral` or `negative`. The results are displayed both numerically and visually (pie chart).

### Tech Stack 📚

* Python (`version==3.10.0`) 
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
-  🎯 Solve the issue with sentiment analysis BERT-classifier. another model? processing entries by batches?

## Limitations & Disclaimer ⚠️

* The sentiment analysis model might not perform well on very large input sizes. For this, only the most recent 200 entries are used when analyzing sentiment on Eksi Sozluk titles with 200+ entries.
* The application EksiSUMM and its creator _(yours truly)_ is not responsible for the factual accuracy of the summary provided. This application mainly focuses on summarizing the (mostly subjective) entries written by users online.

## Contact

For questions and inquiries, you could contact via my `mronatkaya@gmail.com` or [LinkedIn](https://www.linkedin.com/in/onat-kaya2/)


## License
This project is licensed under the MIT License.
