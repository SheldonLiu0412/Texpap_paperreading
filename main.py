from src.core.processor import PaperProcessor
from src.config.settings import PAPERS_DIR

def main():
    try:
        processor = PaperProcessor()
        pdf_path = PAPERS_DIR / "Transformer-xl.pdf"
        tex_path, pdf_path = processor.process_pdf(str(pdf_path))
        print(f"处理完成，结果保存在：")
        print(f"TEX文件：{tex_path}")
        print(f"PDF文件：{pdf_path}")
    except Exception as e:
        print(f"处理失败：{str(e)}")

if __name__ == "__main__":
    main() 