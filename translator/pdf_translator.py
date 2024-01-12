from typing import Optional
from model import Model
from translator.pdf_parser import PDFParser
from translator.writer import Writer
from utils import LOG
from book import ContentType
import io

class PDFTranslator:
    def __init__(self, model: Model):
        self.model = model
        self.pdf_parser = PDFParser()
        self.writer = Writer()

    def translate_pdf(self, pdf_file, file_format: str = 'pdf', to_lan: str = 'Chinese', style: str = 'plain', output_file_path: str = None, pages: Optional[int] = None):
        self.book = self.pdf_parser.parse_pdf(pdf_file, pages)

        for page_idx, page in enumerate(self.book.pages):
            for content_idx, content in enumerate(page.contents):
                translation = None
                status = False
                if content.content_type == ContentType.IMAGE:
                    translation = content.original.original
                    status = True
                    LOG.debug("Image so just reserve the image only")
                else:
                    messages = self.model.translate_messages(content, to_lan = to_lan, style = style)
                    LOG.debug(messages)
                    translation, status = self.model.make_request(messages)
                    LOG.info(translation)
                
                # Update the content in self.book.pages directly
                self.book.pages[page_idx].contents[content_idx].set_translation(translation, status)
        if isinstance(pdf_file, str):
            output_file_path = self.book.pdf_file.replace('.pdf', f'_{to_lan}.{file_format}')
            self.writer.save_translated_book(self.book, output_file_path, file_format)
        else:
            buffer = io.BytesIO()
            self.writer.save_translated_book(self.book, buffer, file_format)
            buffer.seek(0)
            return buffer

