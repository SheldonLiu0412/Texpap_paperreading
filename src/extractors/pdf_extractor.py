import PyPDF2
from typing import Optional

class PdfExtractor:
    @staticmethod
    def extract_text(pdf_path: str) -> Optional[str]:
        """从PDF文件中提取文本"""
        try:
            with open(pdf_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                text = ""
                for page in reader.pages:
                    text += page.extract_text()
                return PdfExtractor.remove_references(text)
        except Exception as e:
            print(f"PDF文本提取失败: {str(e)}")
            return None

    @staticmethod
    def remove_references(text: str) -> str:
        """移除参考文献部分"""
        references_index = text.find('References')
        if references_index != -1:
            return text[:references_index]
        return text 