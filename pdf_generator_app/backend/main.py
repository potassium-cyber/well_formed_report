import os
import shutil
import subprocess
import uuid
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional, Any

app = FastAPI()

# --- 配置 CORS (解决跨域问题) ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 允许任何来源的前端访问 (生产环境建议改为具体的 Netlify 域名)
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有 HTTP 方法 (GET, POST等)
    allow_headers=["*"],  # 允许所有 Header
)

# --- 配置路径 ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATE_DIR = os.path.join(BASE_DIR, "templates")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
TEMP_DIR = os.path.join(BASE_DIR, "temp_builds")

# 确保临时目录存在
os.makedirs(TEMP_DIR, exist_ok=True)

# --- 定义数据模型 ---
class ContentBlock(BaseModel):
    type: str
    title: Optional[str] = None
    content: Optional[str] = None
    path: Optional[str] = None
    caption: Optional[str] = None
    headers: Optional[List[str]] = None
    rows: Optional[List[List[Any]]] = None

class ReportRequest(BaseModel):
    course: str  # 新增字段
    title: str
    title_en: str
# ... (中间字段保持不变)

@app.post("/generate")
async def generate_pdf(request: ReportRequest):
    build_id = str(uuid.uuid4())
    build_dir = os.path.join(TEMP_DIR, build_id)
    os.makedirs(build_dir, exist_ok=True)
    
    try:
        # 2. 智能模版路由
        # 默认使用 paper.typ (如果你保留了它作为通用模版)
        # 或者默认使用 tech_report.typ
        template_name = "paper.typ" 
        
        if request.course in ["创新创造能力训练I", "创新创造能力训练II"]:
            template_name = "tech_report.typ"
        elif request.course == "教育见习":
            template_name = "edu_report.typ"
        else:
            # 兜底：如果没有匹配到，默认用 paper.typ 或 tech_report.typ
            template_name = "paper.typ"

        # 检查模版是否存在
        src_template = os.path.join(TEMPLATE_DIR, template_name)
        if not os.path.exists(src_template):
            # 如果特定的模版还没上传，回退到 main.typ (如果有) 或报错
            # 这里假设我们至少有一个兜底的
            print(f"Template {template_name} not found, using fallback.")
            if os.path.exists(os.path.join(TEMPLATE_DIR, "paper.typ")):
                src_template = os.path.join(TEMPLATE_DIR, "paper.typ")
            elif os.path.exists(os.path.join(TEMPLATE_DIR, "main.typ")):
                src_template = os.path.join(TEMPLATE_DIR, "main.typ")
        
        # 复制选中的模版为 main.typ (这样后面的编译命令不用变)
        shutil.copy2(src_template, os.path.join(build_dir, "main.typ"))
        
        # 3. 复制资源 (字体、图片) 到构建目录
        # Typst 需要在编译时能访问到这些文件
        for item in os.listdir(ASSETS_DIR):
            s = os.path.join(ASSETS_DIR, item)
            d = os.path.join(build_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
        
        # 4. 保存 JSON 数据
        # Typst 模板通过 #let data = json("real_data.json") 读取
        json_path = os.path.join(build_dir, "real_data.json")
        with open(json_path, "w", encoding="utf-8") as f:
            # 使用 model_dump() (Pydantic v2) 或 dict() (v1)
            # 这里的 ensure_ascii=False 很重要，保证中文不被转义
            json.dump(request.model_dump(), f, ensure_ascii=False, indent=2)
            
        # 5. 调用 Typst 编译
        # 命令: typst compile --font-path . main.typ report.pdf
        cmd = [
            "typst", "compile", 
            "--font-path", ".",   # 告诉 Typst 在当前目录找字体 (STXingkai.TTF)
            "main.typ", 
            "report.pdf"
        ]
        
        result = subprocess.run(
            cmd, 
            cwd=build_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        if result.returncode != 0:
            print(f"Typst Error: {result.stderr.decode()}")
            raise HTTPException(status_code=500, detail=f"Typst Compilation Failed: {result.stderr.decode()}")
            
        pdf_path = os.path.join(build_dir, "report.pdf")
        if not os.path.exists(pdf_path):
             raise HTTPException(status_code=500, detail="PDF file not found after compilation.")

        # 6. 返回文件
        return FileResponse(
            pdf_path, 
            filename=f"report_{request.student_id}.pdf",
            media_type="application/pdf"
        )

    except Exception as e:
        print(f"Server Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run(app, host="0.0.0.0", port=port)