import requests
from bs4 import BeautifulSoup
import os

# TOR proxy settings for accessing .onion sites
TOR_PROXY = {
    "http": "socks5h://127.0.0.1:9050",
    "https": "socks5h://127.0.0.1:9050"
}

def search_pdf(book_name, include_dark_web=False):
    """
    Search for publicly available PDFs on the surface web and optionally on the dark web.

    Args:
        book_name (str): The name of the book to search for.
        include_dark_web (bool): Whether to include dark web searches.

    Returns:
        None
    """
    # Surface web search
    query = book_name.replace(" ", "+") + "+filetype:pdf"
    search_url = f"https://www.google.com/search?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }

    print(f"Searching for '{book_name}' PDF versions on the surface web...")
    try:
        response = requests.get(search_url, headers=headers)
        response.raise_for_status()
        pdf_links = extract_pdf_links(response.text)
        download_pdfs(pdf_links, "surface")

        if include_dark_web:
            search_dark_web(book_name)

    except requests.exceptions.RequestException as e:
        print(f"Error while searching on the surface web: {e}")


def extract_pdf_links(html_content):
    """
    Extract PDF links from HTML content.

    Args:
        html_content (str): The HTML content to parse.

    Returns:
        list: A list of PDF links.
    """
    soup = BeautifulSoup(html_content, "html.parser")
    pdf_links = []
    links = soup.find_all("a", href=True)

    for link in links:
        href = link.get("href")
        if "http" in href and ".pdf" in href:
            pdf_url = href.split("&")[0].replace("/url?q=", "")
            pdf_links.append(pdf_url)
    return pdf_links


def search_dark_web(book_name):
    """
    Search for PDFs on the dark web using a Tor connection.

    Args:
        book_name (str): The name of the book to search for.

    Returns:
        None
    """
    query = book_name.replace(" ", "+") + "+filetype:pdf"
    dark_web_search_url = f"http://msydqstlz2kzerdg.onion/search?q={query}"  # Example onion search engine

    print(f"Searching for '{book_name}' on the dark web...")
    try:
        response = requests.get(dark_web_search_url, proxies=TOR_PROXY, timeout=30)
        response.raise_for_status()
        pdf_links = extract_pdf_links(response.text)
        download_pdfs(pdf_links, "darkweb")
    except requests.exceptions.RequestException as e:
        print(f"Error while searching on the dark web: {e}")


def download_pdfs(pdf_links, source):
    """
    Download PDFs from a list of links.

    Args:
        pdf_links (list): List of PDF links to download.
        source (str): The source (surface or dark web).

    Returns:
        None
    """
    if not pdf_links:
        print(f"No PDFs found on the {source}.")
        return

    print(f"Found {len(pdf_links)} PDF(s) on the {source}. Downloading them...")
    os.makedirs(source, exist_ok=True)
    for idx, pdf_url in enumerate(pdf_links):
        filename = os.path.join(source, f"book_version_{idx + 1}.pdf")
        try:
            response = requests.get(pdf_url, stream=True, proxies=(TOR_PROXY if source == "darkweb" else None))
            response.raise_for_status()

            with open(filename, "wb") as pdf_file:
                for chunk in response.iter_content(chunk_size=8192):
                    pdf_file.write(chunk)
            print(f"Saved as '{filename}'.")
        except requests.exceptions.RequestException as e:
            print(f"Error downloading PDF from {pdf_url}: {e}")


# Usage
search_pdf("Every War Must End", include_dark_web=True)
