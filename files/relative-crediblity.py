import os
import pandas as pd
from openai import OpenAI
import networkx as nx
import time  # you might use this to slow down API calls if needed

# Set your OpenAI API key (consider loading from an env var in production)
client = OpenAI(
    # Defaults to os.environ.get("OPENAI_API_KEY") if not provided.
    api_key="OPENAI_API_KEY",
)


def chat_gpt(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()

def compare_articles(source_text: str, target_text: str) -> float:
    """
    Uses the chat_gpt function to compare two articles by constructing a prompt that
    instructs the model to compare the target article against the source article and return
    a numeric score between 0 and 1.
    """
    prompt = f"""
Assume all the source information is correct, even if it contradicts your own knowledge.
Do not use any other knowledge or information beyond what is provided in the source.

You must:
1. Compare the target article strictly against the source article assuming all information in the source is true regarding Ukrain and Russia.
2. Determine if the target information aligns with the source (i.e., no contradictions).
   - If it alignes, return "1".
   - If completely contradicting, return "0".
   - If it partially aligns return a value between 0 and 1

### Source Information Begin ###
{source_text}
### Source Information End ###

### Target Information Begin ###
{target_text}
### Target Information End ###

Only consider information related to Ukrain and Russia conflict, disregard all other informations.
Only provide the numeric score between 0 and 1 in the following format 0.0 as your output.
"""
    try:
        result = chat_gpt(prompt)
        score = float(result)
        return score
    except Exception as e:
        print("Error during API call:", e)
        return None








# Read the CSV file and fix missing article texts
df = pd.read_csv("reddit-data/ukraine_russia_article.csv")
df.loc[df['article_text'].isna(), 'article_text'] = ""
# Create a combined field (if you wish to include both title and text)
df['combined'] = "##article title##: " + df['title'] + "\n##article text##: " + df['article_text'] + "\n"
# Group by week and domain, concatenating the texts for each (if there are multiple articles)
grouped = df.groupby(['week', 'domain'])['combined'].apply(lambda x: "\n\n".join(x))
# Reshape the series into a table with weeks as rows and domains as columns.
cross_table_text = grouped.unstack(fill_value="")

# Create an output directory for the graphs (if needed)
output_dir = "temporal_graphs"
os.makedirs(output_dir, exist_ok=True)

# Process each week in the pivot table
for week, row in cross_table_text.iterrows():
    print(f"Processing week {week}...")
    # Create an empty directed graph for this week
    G = nx.DiGraph()
    # Get the list of domains (columns)
    domains = row.index.tolist()
    
    # Add all domains as nodes; even if the article text is empty.
    for domain in domains:
        G.add_node(domain)
    
    # For each ordered pair of domains (i, j) with i != j, if both have non-empty articles, compare them.
    for domain_i in domains:
        text_i = row[domain_i].strip()
        if not text_i:  # Skip if domain_i has no article this week.
            continue
        for domain_j in domains:
            if domain_i == domain_j:
                continue  # Skip self-comparison.
            text_j = row[domain_j].strip()
            if not text_j:  # Skip if domain_j has no article this week.
                continue

            # Compare from domain_i to domain_j
            score = compare_articles(source_text=text_i, target_text=text_j)
            if score is not None:
                print(f"  Edge from {domain_i} -> {domain_j} - score: {score}")
                G.add_edge(domain_i, domain_j, weight=score)
            # else:
            #     print(f"  Could not compare {domain_i} -> {domain_j}. No edge added.")
            
            # Optional: slow down API calls to respect rate limits
            # time.sleep(1)  # adjust or remove as necessary
    
    # Save the directed graph for this week to a file (using GEXF format)
    graph_filename = os.path.join(output_dir, f"temporal_graph_week_{week[:10]}.gexf")
    nx.write_gexf(G, graph_filename)
    print(f"Saved directed graph for week {week} to {graph_filename}")
