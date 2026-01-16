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
    title: str
    title_en: str
    student_name: str
    student_id: str
    college: str
    major: str
    grade: str
    supervisor: str
    supervisor_en: str
    student_name_en: str
    finish_year: str
    finish_month: str
    abstract_zh: str
    keywords_zh: str
    abstract_en: str
    keywords_en: str
    content_blocks: List[ContentBlock]

@app.post("/generate")
async def generate_pdf(request: ReportRequest):
    # 1. 创建构建目录
    build_id = str(uuid.uuid4())
    build_dir = os.path.join(TEMP_DIR, build_id)
    os.makedirs(build_dir, exist_ok=True)
    
    try:
        # 2. 复制模板 (main.typ) 到构建目录
        shutil.copy2(os.path.join(TEMPLATE_DIR, "main.typ"), build_dir)
        
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