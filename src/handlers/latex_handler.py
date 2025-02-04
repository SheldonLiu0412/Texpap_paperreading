import os
import time
import subprocess
import logging
from pathlib import Path
from typing import Tuple
from src.config.settings import OUTPUT_DIR, LOGS_DIR, LATEX_TEMPLATE

class LatexHandler:
    @staticmethod
    def save_to_tex(text: str, file_prefix: str, logger: logging.Logger = None) -> str:
        """保存处理后的文本为TEX文件"""
        tex_content = LATEX_TEMPLATE % text
        output_path = OUTPUT_DIR / f"{file_prefix}_解析结果.tex"
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(tex_content)
        if logger:
            logger.info(f"TEX文件已保存：{output_path}")
        return str(output_path)

    @staticmethod
    def compile_tex(tex_path: str, original_filename: str, logger: logging.Logger = None) -> str:
        """编译TEX文件为PDF"""
        work_dir = os.path.dirname(tex_path)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        log_file = LOGS_DIR / f"{original_filename}_{timestamp}_compile.txt"
        
        try:
            if logger:
                logger.info(f"开始编译TEX文件：{tex_path}")
            
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"开始编译 {tex_path}\n")
                f.write(f"时间: {time.strftime('%Y-%m-%d %H:%M:%S')}\n\n")
                
                for i in range(2):
                    if logger:
                        logger.info(f"第 {i+1} 次编译")
                    f.write(f"\n第 {i+1} 次编译:\n")
                    result = subprocess.run([
                        'xelatex',
                        '-interaction=nonstopmode',
                        f'-output-directory={work_dir}',
                        tex_path
                    ], capture_output=True, text=True, check=True)
                    
                    # 记录编译输出
                    f.write("\nSTDOUT:\n")
                    f.write(result.stdout)
                    f.write("\nSTDERR:\n")
                    f.write(result.stderr)
                    f.write("\n" + "="*50 + "\n")
                
                f.write(f"\n编译完成\n时间: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                
        except subprocess.CalledProcessError as e:
            # 如果编译失败，也记录错误信息
            with open(log_file, 'a', encoding='utf-8') as f:
                f.write(f"\n编译失败！\n错误代码: {e.returncode}\n")
                f.write("\nSTDOUT:\n")
                f.write(e.stdout)
                f.write("\nSTDERR:\n")
                f.write(e.stderr)
            if logger:
                logger.error(f"编译失败：{str(e)}")
            raise
        finally:
            # 清理编译过程中生成的临时文件
            LatexHandler.cleanup_temp_files(tex_path, logger)
            
        if logger:
            logger.info("编译完成")
        return tex_path.replace('.tex', '.pdf')

    @staticmethod
    def cleanup_temp_files(tex_path: str, logger: logging.Logger = None) -> None:
        """清理编译过程中生成的临时文件"""
        base_name = os.path.splitext(tex_path)[0]
        temp_extensions = ['.aux', '.log', '.out']
        for ext in temp_extensions:
            temp_file = base_name + ext
            if os.path.exists(temp_file):
                try:
                    os.remove(temp_file)
                    if logger:
                        logger.info(f"已删除临时文件：{temp_file}")
                except Exception as e:
                    if logger:
                        logger.warning(f"删除临时文件失败 {temp_file}: {str(e)}") 