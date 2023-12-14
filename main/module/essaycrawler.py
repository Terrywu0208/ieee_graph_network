"""
Copyright © 2023 Chia En Wu (GitHub: terrywu28)

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""


from bs4 import BeautifulSoup
import requests
import re
import pandas as pd
import json
import time
import random
import os
import argparse
import logging

# Set up logging configuration
log_file_path = 'error_log.txt'
logging.basicConfig(filename=log_file_path, level=logging.INFO, format='%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')

# Add a StreamHandler to print logs to the terminal
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
console_handler.setFormatter(formatter)
logging.getLogger().addHandler(console_handler)

def crawl_ieee_paper_authors(essay_code, headers):
    """Crawl authors of an IEEE paper.

    Args:
        essay_code (str): The code identifying the IEEE paper.
        headers (dict): HTTP headers for the request.

    Returns:
        list: List of authors.
    """
    url = f'https://ieeexplore.ieee.org/document/{essay_code}/authors#authors'
    response = make_request(url, headers, 'crawl_ieee_paper_authors')
    return extract_authors(response)

def crawl_ieee_reference(essay_code, headers):
    """Crawl references of an IEEE paper.

    Args:
        essay_code (str): The code identifying the IEEE paper.
        headers (dict): HTTP headers for the request.

    Returns:
        dict: Dictionary containing paper titles and their authors.
    """
    url = f'https://ieeexplore.ieee.org/rest/document/{essay_code}/references'
    response = make_request(url, headers, 'crawl_ieee_reference')
    return extract_references(response)

def get_essay_list(query_text, page_number, headers):
    """Get a list of IEEE papers based on a search query.

    Args:
        query_text (str): The search query.
        page_number (int): The page number of the search results.
        headers (dict): HTTP headers for the request.

    Returns:
        dict: Dictionary containing paper titles and their codes.
    """
    url = "https://ieeexplore.ieee.org/rest/search"
    payload = {
        'newsearch': True,
        'queryText': query_text,
        'highlight': True,
        'returnFacets': ['ALL'],
        'returnType': 'SEARCH',
        'pageNumber': str(page_number)
    }
    response = make_request(url, headers, 'get_essay_list', payload)
    return extract_essay_list(response)

def make_request(url, headers, func_name, data=None):
    """Make an HTTP request and handle exceptions.

    Args:
        url (str): The URL for the HTTP request.
        headers (dict): HTTP headers for the request.
        func_name (str): The name of the calling function.
        data (dict): Data for a POST request (default is None for GET request).

    Returns:
        requests.Response: The HTTP response object.
    """
    try:
        if data is None:
            response = requests.get(url, headers=headers)
        else:
            response = requests.post(url, headers=headers, data=json.dumps(data, ensure_ascii=False).encode('utf-8'))

        process_response(response, func_name)
        return response
    except Exception as e:
        logging.error(f"Error in {func_name}: {e}")
        return None

def process_response(response, func_name):
    """Process the HTTP response.

    Args:
        response (requests.Response): The HTTP response object.
        func_name (str): The name of the calling function.
    """
    if response.status_code != 200:
        logging.error(f"{func_name} failed. Status code: {response.status_code}")
        response.raise_for_status()
    else:
        logging.info(f"{func_name} successful. Status code: {response.status_code}")

def extract_authors(response):
    """Extract authors from the HTML response.

    Args:
        response (requests.Response): The HTML response object.

    Returns:
        list: List of authors.
    """
    soup = BeautifulSoup(response.text, 'html.parser')
    author_tags = soup.find_all('author')
    authors = [author.text.strip() for author in author_tags]

    pattern = re.compile(r'authorNames":"(.*)\"')
    matches = pattern.findall(str(soup))

    if matches:
        authors = [match.strip() for match in matches]
        authors = authors[0].split(",")[0]
        authors = authors.replace('\"', "")
    else:
        logging.error("未找到 authorNames")

    return authors

def extract_references(response):
    """Extract references from the JSON response.

    Args:
        response (requests.Response): The JSON response object.

    Returns:
        dict: Dictionary containing paper titles and their authors.
    """
    data = response.json()
    result_dict = {}

    for ref in range(len(data["references"])):
        text = data["references"][ref]["text"]
        authors_ls = []

        authors_match = re.search(r'([^,]+),([^"]+)"', text)
        if authors_match:
            authors = authors_match.group(0).strip(' ,').replace('"', "")
            authors_comma = authors.split(",")
            for i in authors_comma:
                if i:
                    tmp = i.replace("et al.", "")
                    authors_ls.extend(tmp.split("and"))

        title_match = re.search(r'"([^"]+)"', text)
        if title_match:
            title = title_match.group(1)
            authors_ls = [i.strip() for i in authors_ls if i != ' ']
            cleaned_title = re.sub(r'\[[^\]]+\]', '', title)
            result_dict[cleaned_title] = authors_ls

    return result_dict

def extract_essay_list(response):
    """Extract IEEE papers from the JSON response.

    Args:
        response (requests.Response): The JSON response object.

    Returns:
        dict: Dictionary containing paper titles and their codes.
    """
    response_dict = json.loads(response.content.decode('utf-8'))
    result_dict = {}

    for record in range(len(response_dict["records"])):
        result_dict[response_dict["records"][record]["articleTitle"]] = response_dict["records"][record]["articleNumber"]

    return result_dict

def ieee_crawler(search_keywords, max_pages, file_name=None, sleep_min=5, sleep_max=10, max_retries=2):
    """Main function to crawl IEEE paper data.

    Args:
        search_keywords (list): List of search keywords.
        max_pages (int): Maximum number of pages to crawl.
        file_name (str): Name of the output CSV file.
        headers (dict): HTTP headers for the requests.
        sleep_min (int): Minimum sleep duration between requests.
        sleep_max (int): Maximum sleep duration between requests.
        max_retries (int): Maximum number of retries for failed requests.
    """
    headers = {
            'Accept': 'application/json, text/plain, */*',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'Accept-Language': 'zh-TW,zh;q=0.9,en-US;q=0.8,en;q=0.7',
            'Content-Type': 'application/json',
            'Origin': 'https://ieeexplore.ieee.org',
            'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp?newsearch=true&queryText=LLM',
            'Sec-Ch-Ua': '"Google Chrome";v="119", "Chromium";v="119", "Not?A_Brand";v="24"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'X-Security-Request': 'required'
        }
    data_list = []

    for num in range(1, max_pages):
        logging.info(f"***********************   Page  {num}   ***********************************")
        for search_keyword in search_keywords:
            essay = get_essay_list(search_keyword, num, headers)
            if essay is None:
                continue

            for title, essay_code in essay.items():
                logging.info("-----------------------------------------------------------------------")
                logging.info("essayCode : %s", essay_code)
                retries = 0
                while retries < max_retries:
                    try:
                        time.sleep(4)
                        references = crawl_ieee_reference(essay_code, headers)
                        authors = crawl_ieee_paper_authors(essay_code, headers)
                        if authors is not None and references is not None:
                            logging.info("title : %s", title)
                            logging.info("reference : %s", references)
                            logging.info("authors : %s", authors)
                            data_list.append({
                                'title': title,
                                'essayCode': essay_code,
                                'reference': json.dumps(references),
                                'author': authors
                            })
                        break
                    except Exception as e:
                        retries += 1
                        logging.error(f"Failed with exception: {e}. Retrying...")
                        time.sleep(random.randint(sleep_min, sleep_max))
    df = pd.DataFrame(data_list)
    return df

def main(search_keywords, max_pages, file_name, sleep_min=5, sleep_max=10, max_retries=3):
    df = ieee_crawler(search_keywords, max_pages, file_name, sleep_min, sleep_max, max_retries)
    folder_name = "output_data"
    os.makedirs(folder_name, exist_ok=True)
    csv_file_path = os.path.join(folder_name, f"{file_name}.csv")
    df.to_csv(csv_file_path)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Crawl IEEE paper data.')
    parser.add_argument('--search_keywords', nargs='+', help='Keywords for searching papers (e.g., --search_keywords "social network")')
    parser.add_argument('--max_pages', type=int, help='Maximum number of pages to crawl')
    parser.add_argument('--file_name', help='Name of the output CSV file (e.g., --file_name social_network_data)')

    args = parser.parse_args()

    if not any(vars(args).values()):
        parser.print_help()
    else:

        main(args.search_keywords, args.max_pages, args.file_name)
