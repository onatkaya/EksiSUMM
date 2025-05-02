from bs4 import BeautifulSoup
from urllib.request import Request, urlopen
import re
from openai import OpenAI
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification, AutoModel
from collections import Counter
from peft import PeftModel, PeftConfig
import matplotlib.pyplot as plt
import io
from PIL import Image
import os

api_key = os.environ.get("OPENAI_KEY")

def check_multi_page(url_main):
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

def single_page_scrape(url):
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

def get_page_title(url):
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

def all_pages_scrape(url_main):
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

# Using OpenAI API, for summarization
def get_completion(prompt, tokens_create, model="gpt-4o-mini"):
    client = OpenAI(api_key=api_key)
    messages = [{"role": "user", "content": prompt}]
    response = client.responses.create(
        model=model,
        input=messages,
        temperature=0.1, # this is the degree of randomness of the model's output
        max_output_tokens=tokens_create
    )
    return(response.output_text)

def create_pie_chart(positives, neutrals, negatives):
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
def sentiment_analysis(entries_list):
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

def getSummary(url_main, tokens_create, sentiment, lang="English"):
    url_title = get_page_title(url_main)
    print(f"Title is extracted: {url_title}")
    print(f"Starting to scrape EksiSozluk entries for the title '{url_title}'...")
    entries_list = all_pages_scrape(url_main)
    
    print(f"Generating the summary...\n")
    prompt =  f"""
    You are going to be a presented a list of strings below. Each string in the list is in Turkish. \
    These strings are scraped from a Turkish forum that resembles Reddit, called Ekşi Sözlük. \
    Each string in the list represents a post, under a specified title. The list of strings will be specified under single quotations. \
    The title representing the topic of the posts will also be given below as well (under single quotations). \
    Summarize what is being said in these posts overall, for someone who does not know anything neither about the posts nor the title. \
    Write the summary in {lang}. Use bullet points for better clarity. Please do not have incomplete sentence(s) in the output.
    
    Title: '{url_title}'   
    
    List of strings (posts): '{entries_list}'
    
    """
    if(sentiment==False):
        response = get_completion(prompt=prompt, tokens_create=tokens_create)
        response2 = f"Total number of entries considered: {len(entries_list)}\n" + response 
        return response2, "--", None
    else:
        response = get_completion(prompt=prompt, tokens_create=tokens_create)
        response2 = f"Total number of entries considered: {len(entries_list)}\n" + response
        try:   
            sentiment_result, image = sentiment_analysis(entries_list)
        except: # gives error if >= 250 entries. --> but gave an error in [-245:]?.
            print("***Entered Exception for Sentiment Analysis...***")
            sentiment_result, image = sentiment_analysis(entries_list[-200:])
        return response2, sentiment_result, image