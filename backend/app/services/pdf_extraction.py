from __future__ import annotations

from typing import List
import fitz


class PageText:
    def __init__(self, page_index: int, text: str):
        self.page_index = page_index
        self.text = text


def extract_pages(path: str) -> List[PageText]:
    doc = fitz.open(path)
    pages: List[PageText] = []
    for index in range(len(doc)):
        page = doc.load_page(index)
        text = page.get_text("text")
        pages.append(PageText(page_index=index, text=text))
    doc.close()
    return pages
