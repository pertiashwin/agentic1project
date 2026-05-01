from scholarly import scholarly
import pandas as pd
import feedparser
import time
import os
import requests

# ============================================
# USER INPUT
# ============================================
TOPIC = "Artificial Intelligence in Healthcare"
MAX_PAPERS = 20
OUTPUT_FILE = "research_papers.xlsx"

SEARCH_QUERY = "artificial intelligence"
MAX_RESULTS = 20
OUTPUT_FOLDER = "output"
OUTPUT_FILE = "arxiv_papers.xlsx"
# ============================================
# CREATE OUTPUT FOLDER
# ============================================

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ============================================
# ARXIV API FUNCTION
# ============================================

def fetch_arxiv_papers(query, max_results=10):
    print(f"\nSearching arXiv for: {query}\n")
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{query}"
    start = 0
    max_results_param = f"max_results={max_results}"
    url = f"{base_url}{search_query}&start={start}&{max_results_param}"
    response = requests.get(url)
    feed = feedparser.parse(response.text)
    papers = []
    for i, entry in enumerate(feed.entries, start=1):
        title = entry.title.replace("\n", " ")
        authors = ", ".join(author.name for author in entry.authors)
        published = entry.published
        summary = entry.summary.replace("\n", " ")
        paper_link = entry.link
        pdf_link = ""
        for link in entry.links:
            if link.type == "application/pdf":
                pdf_link = link.href
        category = ", ".join(tag["term"] for tag in entry.tags)
        doi = entry.get("arxiv_doi", "N/A")
        paper_data = {
            "Title": title,
            "Authors": authors,
            "Published": published,
            "Category": category,
            "DOI": doi,
            "Abstract": summary,
            "Paper Link": paper_link,
            "PDF Link": pdf_link
        }

        papers.append(paper_data)
        print(f"[{i}] {title} ")
    return papers
    
# ============================================
# SEARCH FUNCTION
# ============================================

def search_papers(topic, max_papers=10):
    print(f"\nSearching papers for: {topic}\n")
    search_query = scholarly.search_pubs(topic)
    papers_data = []
    count = 0

    while count < max_papers:
        try:
            paper = next(search_query)
            bib = paper.get("bib", {})
            title = bib.get("title", "N/A")
            authors = bib.get("author", "N/A")
            year = bib.get("pub_year", "N/A")
            abstract = bib.get("abstract", "N/A")
            citations = paper.get("num_citations", 0)
            pub_url = paper.get("pub_url", "N/A")
            venue = bib.get("venue", "N/A")
            papers_data.append({
                "Title": title,
                "Authors": authors,
                "Year": year,
                "Citations": citations,
                "Venue": venue,
                "Abstract": abstract,
                "Paper Link": pub_url
            })
            count += 1
            print(f"[{count}] {title}")

            # Prevent blocking
            time.sleep(2)
        except StopIteration:
            print("\nNo more papers found.")
            break
        except Exception as e:
            print(f"\nError: {e}")
    return papers_data

# ============================================
# SAVE TO EXCEL
# ============================================

def save_to_excel(data):
    df = pd.DataFrame(data)
    file_path = os.path.join(OUTPUT_FOLDER, OUTPUT_FILE)
    df.to_excel(file_path, index=False)
    print(f"\nExcel file saved at:\n{file_path}")

# ============================================
# MAIN
# ============================================

if __name__ == "__main__":
    papers = fetch_arxiv_papers(SEARCH_QUERY, MAX_RESULTS)
    if papers:
        save_to_excel(papers)
        print("\nCompleted Successfully!")
    else:
        print("\nNo papers found.")