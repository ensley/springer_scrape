from pathlib import Path
from urllib import parse

import pandas as pd
import requests
from tqdm import tqdm


def read_booklist(fp):
    books = pd.read_excel(fp)
    return books


def stitch_filenames(books):
    titles = books['Book Title'].str.replace('[ //]', '-').tolist()
    author_lastnames = ['-'.join([author.split(' ')[-1] for author in author_set])
                        for author_set in books['Author'].str.split(',')]
    editions = books['Edition'].str.replace('.', '').str.replace(' ', '-').tolist()
    filenames = ['__'.join(elements) for elements in zip(titles, author_lastnames, editions)]
    return filenames


def pull_urls(books):
    urls = books['OpenURL'].tolist()
    return urls


def scrape(urls, filenames, categories):
    base_path = Path('~/Documents/Springer books').expanduser()
    base_path.mkdir(parents=True, exist_ok=True)

    for url, filename, category in tqdm(zip(urls, filenames, categories),
                                        unit='book', total=len(urls)):
        catpath = base_path / category
        catpath.mkdir(exist_ok=True)
        f = (catpath / filename).with_suffix('.pdf')

        if not f.exists():
            r = requests.get(url)
            book_url = parse.unquote(r.url)

            pdf_url = construct_pdf_url(book_url)
            pdf = requests.get(pdf_url)

            with open(f, 'wb') as localfile:
                localfile.write(pdf.content)

            f = f.with_suffix('.epub')
            epub_url = construct_epub_url(book_url)
            epub = requests.get(epub_url)

            if epub.status_code == 200:
                with open(f, 'wb') as localfile:
                    localfile.write(epub.content)



def construct_epub_url(book_url):
    epub_url = parse.urlsplit(book_url)
    epub_url = epub_url._replace(path=epub_url.path.replace('book', 'download/epub') + '.epub')
    epub_url = parse.urlunsplit(epub_url)
    return epub_url


def construct_pdf_url(book_url):
    pdf_url = parse.urlsplit(book_url)
    pdf_url = pdf_url._replace(path=pdf_url.path.replace('book', 'content/pdf'))
    pdf_url = parse.urlunsplit(pdf_url)
    return pdf_url


def pull_categories(books):
    categories = books['English Package Name'].tolist()
    return categories


def main():
    books = read_booklist('Free+English+textbooks.xlsx')
    filenames = stitch_filenames(books)
    urls = pull_urls(books)
    categories = pull_categories(books)
    scrape(urls, filenames, categories)


if __name__ == '__main__':
    main()
