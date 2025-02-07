import newspaper
import time
from tqdm import tqdm

from read_data import *
# Assuming single_topic is a DataFrame containing a column 'url'
def fetch_article_content(url,attempts = 3,delay = 2):
    for attempt in range(attempts):
        try:
            article = newspaper.article(url)
            article.download()
            article.parse()
            return {
                "url": url,
                "title": article.title,
                "text": article.text
            }
        except Exception as e:
            # print(f"\nAttempt {attempt + 1} failed for {url}: {e}")
            if attempt < attempts - 1:
                time.sleep(min(delay, 60))  # Ensure the max delay is 1 minute
                delay *= 2  # Exponential backoff

    return {"url": url, "title": None, "text": None}

# Assuming single_topic DataFrame has a column 'url'

bad_count=0
df=read_plot(file_path='reddit-data/ukraine_russia.csv')
df_loaded=pd.read_csv('reddit-data/ukraine_russia_article.csv')
df["article_title"]=''
df["article_text"]=''
for i, row in tqdm(df.iterrows(), total=len(df)):
    # if row["title"]
    if not df_loaded[row['title']==df_loaded["article_title"]].empty:
        df.at[i, "article_title"] = df_loaded[row['title']==df_loaded["article_title"]]["article_title"]
        df.at[i, "article_text"] = df_loaded[row['title']==df_loaded["article_title"]]["article_text"]
    elif pd.isna(row["article_title"]) or row["article_title"] == '':
        article = fetch_article_content(row["url"])
        if article["title"]:
            df.at[i, "article_title"] = article["title"]
            df.at[i, "article_text"] = article["text"]
        else:
            bad_count+=1
    if i%100==0 and i>0:
        print(2*"\n","*"*100)
        print(f"Processed {i} articles with retrival ratio: {1- bad_count/(i+1)}")
        print("*" * 100,2 * "\n")
        df.to_csv('reddit-data/ukraine_russia_article.csv', index=False)
df.to_csv('reddit-data/ukraine_russia_article.csv', index=False)