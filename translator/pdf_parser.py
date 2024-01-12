import pdfplumber
from typing import Optional
from book import Book, Page, Content, ContentType, TableContent
from translator.exceptions import PageOutOfRangeException
from utils import LOG


class PDFParser:
    def __init__(self):
        pass
    def isInside(self, text_item, contentList):
        source_bbox = (text_item['x0'], text_item['top'], text_item['x1'], text_item['bottom'])
        for c in contentList:
            iou = self.calculate_iou(source_bbox, c.bbox)
            if iou > 0.0:
                return True
        return False
    
    def calculate_iou(self, boxA, boxB):
        # determine the (x, y)-coordinates of the intersection rectangle
        xA = max(boxA[0], boxB[0])
        yA = max(boxA[1], boxB[1])
        xB = min(boxA[2], boxB[2])
        yB = min(boxA[3], boxB[3])

        # compute the area of intersection rectangle
        interArea = abs(max((xB - xA, 0)) * max((yB - yA), 0))
        if interArea == 0:
            return 0
        # compute the area of both the prediction and ground-truth
        # rectangles
        boxAArea = abs((boxA[2] - boxA[0]) * (boxA[3] - boxA[1]))
        boxBArea = abs((boxB[2] - boxB[0]) * (boxB[3] - boxB[1]))

        # compute the intersection over union by taking the intersection
        # area and dividing it by the sum of prediction + ground-truth
        # areas - the interesection area
        iou = interArea / float(boxAArea + boxBArea - interArea)

        # return the intersection over union value
        return iou    
    
    def merge_text(self, texts):
        ret = list()
        prev = None
        for item in texts:
            text = item['text']
            if text.strip() == '':
                if prev is not None:
                    ret.append(prev)
                    prev = None
                continue
            if prev is None:
                prev = item
            else:
                prev['text'] = prev['text'] + text
            if text.strip().endswith('.'):
                ret.append(prev)
                prev = None
        if prev is not None:
            ret.append(prev)
        
        return ret                
    
    def parse_pdf(self, pdf_file, pages: Optional[int] = None) -> Book:
        book = None
        if isinstance(pdf_file, str):
            book = Book(pdf_file)
        else:
            book = Book(pdf_file.filename)

        with pdfplumber.open(pdf_file) as pdf:
            if pages is not None and pages > len(pdf.pages):
                raise PageOutOfRangeException(len(pdf.pages), pages)

            if pages is None:
                pages_to_parse = pdf.pages
            else:
                pages_to_parse = pdf.pages[:pages]

            for pdf_page in pages_to_parse:
                page = Page()
                # 先找出所有tables
                tables = pdf_page.find_tables()
                for t in tables:
                    page.add_content(TableContent(t))
                # 找出所有images
                for i in pdf_page.images:
                    img_bbox = (i['x0'], i['top'], i['x1'], i['bottom'])
                    pil_img = pdf_page.crop(img_bbox).to_image(antialias=True)
                    page.add_content(Content(ContentType.IMAGE, pil_img, img_bbox))
                #找出所有文字
                texts = pdf_page.extract_words(x_tolerance=2, y_tolerance=2, keep_blank_chars=True)
                
                # 过滤在tables中的文字
                texts = filter(lambda x: not self.isInside(x, page.contents), texts)
                
                # 合并未完结的句子
                texts = self.merge_text(texts)

                # 将有效的texts加到page中
                for t in texts:
                    page.add_content(Content(ContentType.TEXT, t, (t['x0'],  t['top'], t['x1'], t['bottom'])))

                # 按出现先后顺序排序
                page.contents.sort(key=lambda x: x.bbox)

                book.add_page(page)

        return book
