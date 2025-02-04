# Texpap 论文解读工具

这是一个自动化的学术论文解读工具，可以将PDF格式的学术论文转换为易于理解的中文解读版本。对论文内容进行AI解读，并附带LaTeX源码。

## 当前支持

- PDF文本提取和预处理
- 智能分节和章节处理
- 公式和数学符号的AI解读
- 自动生成LaTeX文档

## 项目结构

```
texpap_paperreading/
├── Papers/                    # 存放PDF论文
├── output/                    # 输出文件夹
├── logs/                      # 日志文件夹
├── src/                       # 源代码目录
│   ├── config/               # 配置模块
│   ├── core/                 # 核心功能模块
│   ├── extractors/           # 提取器模块
│   ├── handlers/             # 处理器模块
│   └── utils/                # 工具模块
├── main.py                   # 主程序入口
├── requirements.txt          # 依赖文件
└── README.md                # 项目说明文档
```

## 环境要求

- Python 3.9+
- XeLaTeX（用于PDF生成）
- 中文字体支持（SimSun、SimHei、SimFang）

## 安装步骤

1. 克隆仓库：
```bash
git clone https://github.com/SheldonLiu0412/texpap_paperreading.git
cd texpap_paperreading
```

2. 安装依赖：
```bash
pip install -r requirements.txt
```

3. 配置环境变量：
创建 `.env` 文件并设置以下变量：
```
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=your_api_base_url
```

## 使用方法

1. 将要解读的PDF论文放入 `Papers` 目录，并在main函数中修改对应名称

2. 运行程序：
```bash
python main.py
```

3. 查看结果：
- 解读结果将保存在 `output` 目录下
- 处理日志将保存在 `logs` 目录下

## 输出文件

- `{论文名称}_解析结果.tex`：LaTeX源文件
- `{论文名称}_解析结果.pdf`：最终的PDF文档
- `{论文名称}_{时间戳}_process.log`：处理过程日志
- `{论文名称}_{时间戳}_compile.txt`：编译日志

## 日志系统

系统提供两种类型的日志：
1. 处理日志：记录整个解析过程的详细信息
2. 编译日志：记录LaTeX编译过程的信息

## 注意事项

- 确保系统已安装XeLaTeX
- 确保系统安装了所需的中文字体
- PDF文件不要超过25个文本块（约60页）
- 确保网络连接稳定（需要访问AI服务）

## 错误处理

常见错误及解决方案：
1. "无法提取PDF文本"
   - 检查PDF文件是否损坏
   - 确认PDF文件是文本格式而非扫描版

2. "文档过长，超出处理限制"
   - 尝试处理论文的部分章节
   - 调整配置文件中的 `MAX_CHUNKS` 参数

3. LaTeX编译错误
   - 检查日志文件中的具体错误信息
   - 确保所需的LaTeX包都已安装

## 贡献指南

欢迎提交Pull Request来改进项目。在提交之前，请确保：
1. 代码符合项目的编码规范
2. 更新了相关文档

## 许可证

MIT License
