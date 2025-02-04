from typing import List
import re
from src.config.settings import DEFAULT_CHUNK_SIZE, MIN_CHUNK_SIZE

class TextProcessor:
    @staticmethod
    def split_into_chunks(text: str, chunk_size: int = DEFAULT_CHUNK_SIZE) -> List[str]:
        """将文本分割成块"""
        return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

    @staticmethod
    def merge_small_chunks(chunks: List[str]) -> List[str]:
        """合并小于指定大小的文本块"""
        if len(chunks) <= 1:
            return chunks

        merged_chunks = [chunks[0]]
        for i in range(1, len(chunks)):
            current_chunk = chunks[i]
            if len(current_chunk) < MIN_CHUNK_SIZE:
                merged_chunks[-1] += current_chunk
            else:
                merged_chunks.append(current_chunk)

        print(f"合并小块后，文本块数量从 {len(chunks)} 减少到 {len(merged_chunks)}")
        return merged_chunks

    @staticmethod
    def clean_text_for_processing(text: str) -> str:
        """清理和标准化文本"""
        return text.replace('\s+', ' ').strip()

    @staticmethod
    def clean_text_for_latex(text: str) -> str:
        """清理文本以用于LaTeX"""
        cleaned_text = text
        # 移除代码块标记和其他无关文本
        cleaned_text = cleaned_text.replace('```', '')\
            .replace('latex', '')\
            .replace('抱歉，我无法处理该请求', '')
        
        # 处理特殊字符
        cleaned_text = re.sub(r'(?<!\\)%', r'\\%', cleaned_text)  # 处理百分号
        cleaned_text = re.sub(r'(?<!\\)&', r'\\&', cleaned_text)  # 处理&符号
        cleaned_text = re.sub(r'(?<!\\)#', r'\\#', cleaned_text)  # 处理#符号
        cleaned_text = re.sub(r'\\\\([{}])', r'\\\1', cleaned_text)  # 清理双重转义的花括号
        
        return cleaned_text 