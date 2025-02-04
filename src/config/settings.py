import os
from pathlib import Path
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 基础路径配置
PROJECT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
OUTPUT_DIR = PROJECT_ROOT / "output"
LOGS_DIR = PROJECT_ROOT / "logs"
PAPERS_DIR = PROJECT_ROOT / "Papers"

# OpenAI配置
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL")
DEFAULT_MODEL = "gpt-4o-mini"

# PDF处理配置
MAX_CHUNKS = 25
MIN_CHUNK_SIZE = 1500
DEFAULT_CHUNK_SIZE = 7000

# LaTeX配置
LATEX_TEMPLATE = """
\\documentclass[12pt]{article}
\\usepackage{xeCJK}
\\usepackage{graphicx}
\\usepackage{amsmath}
\\usepackage{amssymb}
\\usepackage{hyperref}
\\usepackage{url}

\\setCJKmainfont{SimSun}
\\setCJKsansfont{SimHei}
\\setCJKmonofont{SimFang}

\\usepackage[top=2.54cm, bottom=2.54cm, left=2.54cm, right=2.54cm]{geometry}
\\usepackage{titlesec}
\\titleformat*{\\section}{\\large\\bfseries}
\\titleformat*{\\subsection}{\\normalsize\\bfseries}

\\linespread{1.5}

\\begin{document}

%s

\\end{document}
"""

# 创建必要的目录
for dir_path in [OUTPUT_DIR, LOGS_DIR, PAPERS_DIR]:
    if not dir_path.exists():
        dir_path.mkdir(parents=True)
        print(f"创建目录：{dir_path}") 