import os
import re
import time
import logging
from typing import Tuple, Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential
from src.config.settings import DEFAULT_MODEL, LOGS_DIR

class Logger:
    @staticmethod
    def setup(filename: str) -> logging.Logger:
        """设置日志记录器"""
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"{filename}_{timestamp}_process.log"
        
        # 创建日志记录器
        logger = logging.getLogger(filename)
        logger.setLevel(logging.INFO)
        
        # 创建文件处理器
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # 创建控制台处理器
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # 创建格式化器
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # 添加处理器
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        return logger

class AIHelper:
    def __init__(self, client: OpenAI):
        self.client = client

    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def process_chunk(self, chunk: str, index: int, total_chunks: int, timeout: int = 300) -> Optional[str]:
        """处理单个文本块"""
        try:
            print(f"开始处理第 {index + 1}/{total_chunks} 个文本块")
            
            prompt = '请对以下论文片段中每个完整的小节(如1.1视为一个章节）进行通俗易懂并条理清晰的解读(不对标题、作者、表格、参考文献进行解读)，解读要详略得当（不重要的部分简单概括即可，涉及公式和实现方法要详细解读）。只需要返回[小节（有数字编号优先使用原文的数字编号）]+[片段内容的解读（包含全部公式的详细解读）]。输出为中文且使用latex语言的格式包装，每一节内容解析为一个section，如\\section*，公式独立行展示，而一段话中的数学符号则用美元符号包裹，如"具有$O(N^2)$的时间"。注意！1. 分数命令的正确格式是：分子和分母都需要用花括号括起来；2. 对于较长的公式和不等式，请适当简化，避免单个公式过长。\\n\\n{chunk}'

            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt.format(chunk=chunk)}],
                temperature=0,
                timeout=timeout
            )
            
            result = response.choices[0].message.content
            if result and len(result) > 0:
                print(f"成功处理第 {index + 1}/{total_chunks} 个文本块")
                return result
            else:
                raise Exception("处理结果为空或无效")
                
        except Exception as e:
            print(f"处理第 {index + 1}/{total_chunks} 个文本块失败：{str(e)}")
            raise

    def find_last_incomplete_section(self, chunk: str) -> Optional[str]:
        """识别文本块中最后一个不完整的小节"""
        prompt = '这是论文的一部分，我需要保留其中完整的章节，所以请识别文本块中最后一个不完整的小节，并只返回该小节的节名（因为我后续要做文本的精确匹配，所以请严格保持小节名的名称格式!不允许修改大小写和增减空格!）。如果没有不完整的小节，请返回"无"。\\n\\n{chunk}'
        
        try:
            response = self.client.chat.completions.create(
                model=DEFAULT_MODEL,
                messages=[{"role": "user", "content": prompt.format(chunk=chunk)}],
                temperature=0
            )
            result = response.choices[0].message.content.strip()
            return None if result == "无" else result
        except Exception as e:
            print(f"查找不完整小节时出错：{str(e)}")
            return None

def find_section_using_regex(text: str, section_name: str) -> Tuple[int, Optional[str]]:
    """使用正则表达式查找章节位置"""
    print(f"\n尝试匹配小节名：{section_name}")
    print(f"文本块前200字符：{text[:200]}")

    escaped_name = re.escape(section_name)
    pattern = "(" + escaped_name + "|" + escaped_name.replace('\\s+', '\\s*') + ")"
    regex = re.compile(pattern, re.IGNORECASE)

    match = regex.search(text)
    if match:
        print(f"找到匹配：{match.group()}，位置：{match.start()}")
        return match.start(), match.group()
    else:
        print("未找到精确匹配，尝试模糊匹配")
        words = section_name.split()
        loose_pattern = '\\s*'.join(re.escape(word) for word in words)
        loose_regex = re.compile(loose_pattern, re.IGNORECASE)
        loose_match = loose_regex.search(text)
        
        if loose_match:
            print(f"找到宽松匹配：{loose_match.group()}，位置：{loose_match.start()}")
            return loose_match.start(), loose_match.group()
        
        print("未找到任何匹配")
        return -1, None

def get_file_prefix(filename: str) -> str:
    """从文件名中获取前缀"""
    return os.path.splitext(filename)[0][:12] 