import os, io, re
from typing import List, Tuple
import pysbd
from bs4 import BeautifulSoup
from ebooklib import epub
from docx import Document as Docx
from pdfminer.high_level import extract_text as pdf_extract_text
from pypdf import PdfReader

#Extract text from various file formats (pdf,docx,epub) using the appropriate libraries.
def extract_text(path: str) -> str:
    ext = os.path.splitext(path.lower())[1]
    if ext == '.pdf':
        try:
            return pdf_extract_text(path) or ''
        except Exception:
            r = PdfReader(path)
            return '\n'.join(page.extract_text() or '' for page in r.pages)
    if ext == '.docx':
        d = Docx(path)
        return '\n'.join(p.text for p in d.paragraphs)
    if ext == '.epub':
        book = epub.read_epub(path)
        texts = []
        for item in book.get_items():
            if item.get_type() == epub.ITEM_DOCUMENT:
                soup = BeautifulSoup(item.get_content(), 'html.parser')
                texts.append(soup.get_text(separator=' ', strip=True))
        return '\n'.join(texts)
    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.read()

'''
Clean the extracted text by removing excessive whitespace and newlines.
Removes spaces before newlines.
Limits multiple newlines to at most 2.
Collapses multiple spaces/tabs to a single space.
Returns a clean string ready for chunking.
'''
def clean_text(s: str) -> str:
    s = re.sub(r'\s+\n', '\n', s)
    s = re.sub(r'\n{2,}', '\n\n', s)
    s = re.sub(r'[ \t]+', ' ', s)
    return s.strip()
    
#Split the cleaned text into chunks based on sentence boundaries, ensuring each chunk does not exceed a specified character limit.
def to_chunks(text: str, lang: str='en', target_chars: int=1800) -> List[str]:
    #pysbd 2 split text into sentences.
    seg = pysbd.Segmenter(language=lang, clean=True) #remove unecessary space wit clean flag
    sents = seg.segment(text)
    #chunks → final list of text chunks, cur → current sentences in the chunk, cur_len → current chunk length in characters
    chunks, cur, cur_len = [], [], 0
    #Loop through sentences; skip empty ones.
    for s in sents:
        s = s.strip()
        if not s: continue
        #If adding this sentence exceeds target character limit, save current chunk , start a new one
        if cur_len + len(s) > target_chars and cur:
            chunks.append(' '.join(cur))
            cur, cur_len = [], 0
        cur.append(s); cur_len += len(s) + 1 #Add sentence to current chunk.
    if cur: chunks.append(' '.join(cur))
    return chunks