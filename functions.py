from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
import ollama
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
from collections import Counter
from peft import PeftModel, PeftConfig
import matplotlib.pyplot as plt
import io
from PIL import Image
import os
from typing import List, Optional, Tuple

OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "qwen2.5:3b")
OLLAMA_NUM_CTX = int(os.environ.get("OLLAMA_NUM_CTX", "16384"))


def check_multi_page(url_main: str) -> Tuple[bool, int]:
    """
    Checks whether the page of the title is multi-paged (contains a page counter),
    or single-paged (does not contain a page counter). Returns a boolean, TRUE for multi-paged situations.

    Also: returning the total number of pages (it is 1 for single pages).

    RETURN: tuple containing a boolean and an int.
    """
    
    headers1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'}
    req = Request(url_main, headers=headers1)
    webpage=urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    
    try:
        count = soup.find_all('div', class_ = "pager")[0]  
        temp = str(count)
        data_pagecount_index = temp.index("data-pagecount")
        first_comma = temp.index("\"", data_pagecount_index)
        second_comma = temp.index("\"", first_comma+1)
        pagecount_int = int(temp[first_comma+1:second_comma])
        print(f"This title contains {pagecount_int} pages.")
        return True, pagecount_int # it is multi-paged.
    except:
        print("This title only contains 1 page.")
        return False, 1 # it is single-paged.

def single_page_scrape(url: str) -> List[str]:
    """
    Scraping all the entries from a single URL page.

    RETURN: A list of strings. Each string represents a post from the single page specified.
    """
    headers1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'}
    req = Request(url, headers=headers1)
    webpage=urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    entries = soup.find_all('div', class_ ='content') # have all entries in an iterable (raw, needs further processing)
    entry_list = [a.text.strip() for a in entries] # going through each entry (processing). cleaning it by using .text attribute.
    return entry_list

def get_page_title(url: str) -> str:
    """
    In EksiSozluk, there is a title for the pages.

    This function returns the title, in str format.
    """
    headers1 = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36'}
    req = Request(url, headers=headers1)
    webpage=urlopen(req).read()
    soup = BeautifulSoup(webpage, 'html.parser')
    title = soup.find('span', itemprop='name').text # have all entries in an iterable (raw, needs further processing)
    return str(title)

def all_pages_scrape(url_main: str) -> List[str]:
    """
    Scraping all the entries from all pages.

    RETURN: A list strings. Each string represents a post. Scraped through all pages possible.
    """
    multi_page_bool, num_pages = check_multi_page(url_main)
    all_entries = []
    if(multi_page_bool == True):
        for page in range(num_pages):
            print(f"Scraping page {page+1}...")
            temp_url = url_main + "?p=" + str(page+1)
            temp_entries = single_page_scrape(temp_url)
            all_entries.extend(temp_entries)
    else:
        all_entries.extend(single_page_scrape(url_main))

    print("Scraping EksiSozluk entries is completed!")
    return all_entries

# Using a local Ollama model, for summarization
def get_completion(prompt: str, tokens_create: int, model: str = OLLAMA_MODEL) -> str:
    """
    Sends a prompt to a local Ollama model and retrieves the generated completion.

    RETURN: The model's output text, as a str.
    """


    messages = [{"role": "user", "content": prompt}]
    print(messages)

    response = ollama.chat(
        model=model,
        messages=messages,
        options={
            "temperature": 0.1, # this is the degree of randomness of the model's output
            "num_predict": tokens_create,
            "num_ctx": OLLAMA_NUM_CTX # prompt + output must fit within this, or Ollama silently truncates
        }
    )
    print(response)
    return response["message"]["content"]

def create_pie_chart(positives: int, neutrals: int, negatives: int) -> Image.Image:
    """
    Builds a pie chart visualizing the counts of positive, neutral, and negative posts.

    RETURN: A PIL Image containing the rendered pie chart.
    """
    labels = ['positive', 'neutral', 'negative']
    sizes = [positives, neutrals, negatives]
    colors = ['lightgreen', 'skyblue', 'salmon']
    explode = (0.1, 0.1, 0.1)  # Highlight students

    fig, ax = plt.subplots(figsize=(6, 6))
    ax.pie(sizes, colors=colors, explode=explode, startangle=140, autopct=lambda p: f'{p:.1f}%' if p > 0 else '')
    ax.legend(labels, loc="best")
    ax.set_title('Sentiment Analysis Results')
    ax.axis('equal')  
    
    # Put the figure through a buffer, and then convert it to a Image
    im_buf = io.BytesIO()
    plt.savefig(im_buf, format='png')
    plt.close(fig)
    im_buf.seek(0)
    image  = Image.open(im_buf)
    return image

# https://huggingface.co/VRLLab/TurkishBERTweet
def sentiment_analysis(entries_list: List[str]) -> Tuple[str, Image.Image]:
    """
    Runs sentiment analysis on a list of posts using the TurkishBERTweet
    sentiment classifier, then tallies the results into a pie chart.

    RETURN: A tuple containing a summary string of the sentiment counts
    and a PIL Image of the corresponding pie chart.
    """
    print("Conducting Sentiment Analysis on Posts...")
    peft_model = "VRLLab/TurkishBERTweet-Lora-SA"
    peft_config = PeftConfig.from_pretrained(peft_model)

    # loading Tokenizer
    padding_side = "right"
    tokenizer = AutoTokenizer.from_pretrained(peft_config.base_model_name_or_path, padding_side=padding_side)
    if getattr(tokenizer, "pad_token_id") is None:
        tokenizer.pad_token_id = tokenizer.eos_token_id

    id2label_sa = {0: "negative", 2: "positive", 1: "neutral"}
    turkishBERTweet_sa = AutoModelForSequenceClassification.from_pretrained(peft_config.base_model_name_or_path, return_dict=True, num_labels=len(id2label_sa), id2label=id2label_sa)
    turkishBERTweet_sa = PeftModel.from_pretrained(turkishBERTweet_sa, peft_model)

    label_list = []
    with torch.no_grad():
        for s in entries_list:
            ids = tokenizer.encode_plus(s, return_tensors="pt")
            label_id = turkishBERTweet_sa(**ids).logits.argmax(-1).item()
            label_list.append(id2label_sa[label_id])
    counter_list = Counter(label_list)
    result = f"Total Entries Considered (most recent): {len(label_list)}\n\n\tPositive posts: {counter_list['positive']}\n\tNeutral Posts: {counter_list['neutral']}\n\tNegative Posts: {counter_list['negative']}"
    image = create_pie_chart(counter_list['positive'], counter_list['neutral'], counter_list['negative'])
    return result, image

def getSummary(url_main: str, tokens_create: int, sentiment: bool, lang: str = "English") -> Tuple[str, str, Optional[Image.Image]]:
    """
    Scrapes all entries for a EksiSozluk title and generates an AI summary,
    optionally including sentiment analysis over the scraped posts.

    RETURN: A tuple of (summary string, sentiment result string or "--" if
    sentiment analysis was skipped, pie chart Image or None if skipped).
    """
    url_title = get_page_title(url_main)
    print(f"Title is extracted: {url_title}")
    print(f"Starting to scrape EksiSozluk entries for the title '{url_title}'...")
    entries_list = all_pages_scrape(url_main)
    
    print(f"Generating the summary...\n")
    prompt_old =  f"""
    You are going to be a presented a list of strings below. Each string in the list is in Turkish. \
    These strings are scraped from a Turkish forum that resembles Reddit, called Ekşi Sözlük. \
    Each string in the list represents a post, under a specified title. The list of strings will be specified under single quotations. \
    The title representing the topic of the posts will also be given below as well (under single quotations). \
    Summarize what is being said in these posts overall, for someone who does not know anything neither about the posts nor the title. \
    Write the summary in {lang}. Use bullet points for better clarity. Do not have incomplete sentence(s) in the output! Do not repeat yourself!
    
    Title: '{url_title}'   
    
    List of strings (posts): '{entries_list}'
    
    """

    prompt =  f"""
    Aşağıda bir dizi metin sunulacak. Listedeki her bir metin Türkçe olup, Türkçe bir forum olan Ekşi Sözlük'ten alınmıştır. \
    Listedeki her bir metin, belirli bir başlık altında yapılmış bir paylaşımı temsil etmektedir.
    Metin listesi tek tırnak işaretleri arasında verilecektir. \
    Paylaşımların konusunu belirten başlık da yine aşağıda (tek tırnak işaretleri içinde) sunulacaktır. \
    Ne paylaşımlar ne de başlık hakkında hiçbir bilgisi olmayan birine yönelik olarak, bu paylaşımlarda genel hatlarıyla nelerden bahsedildiğini özetleyin. \
    Özet Türkçe dilinde olsun. \
    Daha anlaşılır olması için madde işaretleri kullan.\
    Çıktıda eksik cümlelere yer vermeyin! Kendini tekrar etme!

    Ekşi Sözlük Başlığı: '{url_title}'   
    
    Metin dizisi (Ekşi sözlük gönderileri): '{entries_list}'
    
    """


    if(sentiment==False):
        response = get_completion(prompt=prompt, tokens_create=tokens_create)
        response2 = f"Başlık Altındaki Toplam Entry Sayısı: {len(entries_list)}\n" + response 
        return response2, "--", None
    else:
        response = get_completion(prompt=prompt, tokens_create=tokens_create)
        response2 = f"Başlık Altındaki Toplam Entry Sayısı: {len(entries_list)}\n" + response
        try:   
            sentiment_result, image = sentiment_analysis(entries_list)
        except: # gives error if >= 250 entries. --> but gave an error in [-245:]?.
            print("***Entered Exception for Sentiment Analysis...***")
            sentiment_result, image = sentiment_analysis(entries_list[-200:])
        return response2, sentiment_result, image