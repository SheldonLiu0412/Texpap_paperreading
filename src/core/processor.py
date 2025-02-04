import os
from typing import Tuple
from openai import OpenAI
from src.config.settings import OPENAI_API_KEY, OPENAI_BASE_URL, MAX_CHUNKS
from src.extractors.pdf_extractor import PdfExtractor
from src.handlers.text_processor import TextProcessor
from src.handlers.latex_handler import LatexHandler
from src.utils.helpers import AIHelper, get_file_prefix, find_section_using_regex, Logger

class PaperProcessor:
    def __init__(self):
        if not all([OPENAI_API_KEY, OPENAI_BASE_URL]):
            raise ValueError("请设置所需的环境变量 OPENAI_API_KEY 和 OPENAI_BASE_URL")
        
        self.client = OpenAI(api_key=OPENAI_API_KEY, base_url=OPENAI_BASE_URL)
        self.ai_helper = AIHelper(self.client)
        
    def process_pdf(self, pdf_path: str) -> Tuple[str, str, str]:
        """处理PDF文件的主函数
        
        Returns:
            Tuple[str, str, str]: 返回(tex文件路径, pdf文件路径, markdown文件路径)
            注意：如果PDF编译失败，pdf_path将为None
        """
        try:
            # 获取原始文件名并设置日志
            original_filename = os.path.basename(pdf_path)
            logger = Logger.setup(original_filename)
            
            logger.info(f"开始处理PDF文件：{pdf_path}")
            
            # 提取文本
            logger.info("开始提取PDF文本")
            text = PdfExtractor.extract_text(pdf_path)
            if not text:
                logger.error("无法提取PDF文本")
                raise Exception("无法提取PDF文本")
            logger.info("PDF文本提取成功")

            # 分块处理（这里我把识别关了，即设置为0）
            logger.info("开始文本分块")
            chunks = TextProcessor.split_into_chunks(text)
            if len(chunks) > MAX_CHUNKS:
                logger.error(f"文档过长，超出处理限制（当前块数：{len(chunks)}，最大限制：{MAX_CHUNKS}）")
                raise Exception("文档过长，超出处理限制")
            if len(chunks) <= 0:
                logger.error("识别到内容非论文")
                raise Exception("识别到内容非论文")

            logger.info(f"初始文本块数量：{len(chunks)}")
            
            # 处理不完整的章节
            logger.info("开始处理不完整章节")
            for i in range(len(chunks) - 1):
                logger.info(f"\n检查第 {i + 1}/{len(chunks)} 个文本块")
                last_incomplete_section = self.ai_helper.find_last_incomplete_section(chunks[i])
                logger.info(f"找到的最后不完整小节名：{last_incomplete_section or '无'}")
                
                if last_incomplete_section:
                    index, match = find_section_using_regex(chunks[i], last_incomplete_section)
                    if index != -1:
                        incomplete_part = chunks[i][index:]
                        chunks[i] = chunks[i][:index]
                        chunks[i + 1] = incomplete_part + chunks[i + 1]
                        logger.info(f"转移到下一小节的前20个字符：{incomplete_part[:20]}")
                    else:
                        logger.warning(f"未找到不完整小节 {last_incomplete_section} 在当前文本块中的位置")
                else:
                    logger.info("当前文本块没有不完整的小节")

            # 合并小文本块
            logger.info("开始合并小文本块")
            chunks = TextProcessor.merge_small_chunks(chunks)
            logger.info(f"合并后的文本块数量：{len(chunks)}")

            # 处理每个文本块
            logger.info("开始处理文本块")
            processed_chunks = []
            for i, chunk in enumerate(chunks):
                cleaned_chunk = TextProcessor.clean_text_for_processing(chunk)
                logger.info(f"处理第 {i + 1}/{len(chunks)} 个文本块")
                result = self.ai_helper.process_chunk(cleaned_chunk, i, len(chunks))
                if result:
                    processed_chunks.append(result)
                    logger.info(f"第 {i + 1} 个文本块处理成功")
                logger.info(f"处理进度：{int((i + 1) / len(chunks) * 100)}%")

            if not processed_chunks:
                logger.error("处理文本失败")
                raise Exception("处理文本失败")

            # 生成最终文档
            logger.info("开始生成最终文档")
            processed_text = "\n\n".join(processed_chunks)
            cleaned_text = TextProcessor.clean_text_for_latex(processed_text)
            file_prefix = get_file_prefix(original_filename)
            
            # 保存和编译
            logger.info("开始保存TEX文件")
            tex_path = LatexHandler.save_to_tex(cleaned_text, file_prefix, logger)
            logger.info(f"TEX文件保存成功：{tex_path}")
            
            # 生成Markdown文件
            logger.info("开始生成Markdown文件")
            md_path = LatexHandler.convert_to_markdown(cleaned_text, file_prefix, logger)
            logger.info(f"Markdown文件生成成功：{md_path}")
            
            # 尝试编译PDF，但不中断执行
            pdf_path = None
            try:
                logger.info("开始编译PDF文件")
                pdf_path = LatexHandler.compile_tex(tex_path, original_filename, logger)
                logger.info(f"PDF文件编译成功：{pdf_path}")
            except Exception as e:
                logger.error(f"PDF编译失败：{str(e)}")
                logger.info("继续执行，返回其他文件路径")
            
            return tex_path, pdf_path, md_path

        except Exception as e:
            if 'logger' in locals():
                logger.error(f"处理PDF时出错: {str(e)}")
            else:
                print(f"处理PDF时出错: {str(e)}")
            raise 