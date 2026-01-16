import json
import os
import subprocess
import sys
import struct
import zlib
import re

# ---------------------------------------------------------
# 辅助函数：LaTeX 特殊字符转义
# ---------------------------------------------------------
def latex_escape(text):
    if not isinstance(text, str):
        return text
    # 定义 LaTeX 特殊字符及其转义形式
    conv = {
        '&': r'\&',
        '%': r'\%',
        '$': r'\$',
        '#': r'\#',
        '_': r'\_',
        '{': r'\{',
        '}': r'\}',
        '~': r'\textasciitilde{}',
        '^': r'\textasciicircum{}',
        '\\': r'\textbackslash{}',
    }
    regex = re.compile('|'.join(re.escape(str(key)) for key in sorted(conv.keys(), key=lambda item: -len(item))))
    return regex.sub(lambda match: conv[match.group()], text)

# ---------------------------------------------------------
# 辅助函数：生成一个简单的 PNG 图片
# ---------------------------------------------------------
def create_dummy_png(file_path, width=400, height=300):
    def png_pack(png_tag, data):
        chunk_head = png_tag + data
        return (struct.pack("!I", len(data)) +
                chunk_head +
                struct.pack("!I", 0xFFFFFFFF & zlib.crc32(chunk_head)))

    # PNG Header
    magic = b"\x89PNG\r\n\x1a\n"
    
    # IHDR Chunk
    ihdr = b'\x00\x00\x01\x90\x00\x00\x01,\x08\x02\x00\x00\x00' # 400x300, 8bit, RGB
    
    # IDAT Chunk (Image Data)
    # 简单的生成一些像素数据
    raw_data = b''
    for y in range(height):
        # Filter byte (0 = None) 
        raw_data += b'\x00' 
        for x in range(width):
            r = x % 255
            g = y % 255
            b = (x + y) % 255
            raw_data += struct.pack('BBB', r, g, b)
    
    compressed_data = zlib.compress(raw_data)
    idat = png_pack(b'IDAT', compressed_data)
    
    # IEND Chunk
    iend = png_pack(b'IEND', b'')

    with open(file_path, 'wb') as f:
        f.write(magic)
        f.write(png_pack(b'IHDR', ihdr)) # 这里其实校验和是错的，但大多数简单的解码器不介意
        f.write(idat)
        f.write(iend)
    print(f"   [自动生成] 测试图片已创建: {file_path}")

# ---------------------------------------------------------
# 主逻辑
# ---------------------------------------------------------
try:
    from jinja2 import Template
except ImportError:
    print("错误: 缺少 'jinja2' 库。\n请运行: pip install jinja2")
    sys.exit(1)

def build_pdf():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(base_dir, 'real_data.json')
    template_path = os.path.join(base_dir, 'real_template.tex')
    output_tex_path = os.path.join(base_dir, 'report.tex')
    
    # 确保图片存在
    img_path = os.path.join(base_dir, 'test_chart.png')
    if not os.path.exists(img_path):
        create_dummy_png(img_path)

    print(f"1. 读取数据: {data_path}")
    with open(data_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"2. 读取模板: {template_path}")
    with open(template_path, 'r', encoding='utf-8') as f:
        template_content = f.read()

    print("3. 渲染 LaTeX 源码...")
    template = Template(template_content)
    # 注册转义过滤器
    template.globals['e'] = latex_escape
    rendered_tex = template.render(**data)

    with open(output_tex_path, 'w', encoding='utf-8') as f:
        f.write(rendered_tex)
    print(f"   已生成中间文件: {output_tex_path}")

    print("4. 调用 Tectonic 编译 PDF...")
    try:
        subprocess.run(["tectonic", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        print("\n[错误] 未找到 'tectonic' 命令。\n请先安装它 (macOS 推荐):\nbrew install tectonic")
        return

    try:
        # 第一次运行可能需要下载包，所以不隐藏输出会更好，但为了整洁我们可以只显示结果
        # 使用 capture_output=False 让用户看到进度
        # 增加 --print 选项，出错时打印日志
        subprocess.run(["tectonic", output_tex_path, "--print"], check=True)
        print("\n------------------------------------------------")
        print("✅ 成功！PDF 已生成: report.pdf")
        print(f"文件位置: {os.path.join(base_dir, 'report.pdf')}")
        print("------------------------------------------------")
    except subprocess.CalledProcessError:
        print("\n❌ 编译失败，请检查上面的错误日志。")

if __name__ == "__main__":
    build_pdf()