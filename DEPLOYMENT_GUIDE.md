# PDF 生成器部署指南

恭喜！你已经完成了项目的开发。本指南将教你如何零成本将项目部署到互联网上。

## 1. 准备工作

你需要拥有以下账号（全部免费）：
*   **GitHub**: 用于托管代码。
*   **Netlify** (或 Vercel): 用于部署前端。
*   **Render** (或 Fly.io): 用于部署后端。

---

## 2. 推送代码到 GitHub

1.  在 GitHub 上新建一个仓库（例如 `pdf-generator`）。
2.  在本地项目根目录下运行：
    ```bash
    git init
    git add .
    git commit -m "Initial commit"
    git branch -M main
    git remote add origin https://github.com/你的用户名/pdf-generator.git
    git push -u origin main
    ```

---

## 3. 部署后端 (Render)

1.  登录 [Render Dashboard](https://dashboard.render.com/)。
2.  点击 **"New"** -> **"Web Service"**。
3.  连接你的 GitHub 仓库。
4.  设置如下：
    *   **Root Directory**: `pdf_generator_app/backend`  (注意：这很重要，因为我们的 Dockerfile 在这里)
    *   **Environment**: Docker
    *   **Region**: Singapore (离国内近) 或 US
5.  点击 **"Create Web Service"**。
6.  等待几分钟，部署完成后，你会在左上角看到一个 URL（例如 `https://pdf-backend-xyz.onrender.com`）。**复制这个网址**。

---

## 4. 部署前端 (Netlify)

1.  登录 [Netlify](https://www.netlify.com/)。
2.  点击 **"Add new site"** -> **"Import an existing project"**。
3.  连接 GitHub。
4.  设置如下：
    *   **Base directory**: `pdf_generator_app/frontend`
    *   **Build command**: `npm run build`
    *   **Publish directory**: `dist`
5.  **关键步骤：设置环境变量**
    *   点击 **"Show advanced"** 或在部署后的 "Site settings" -> "Environment variables"。
    *   添加变量名：`VITE_API_URL`
    *   变量值：粘贴你刚才复制的后端网址（**不要**带最后的 `/`，例如 `https://pdf-backend-xyz.onrender.com`）。
6.  点击 **"Deploy site"**。

---

## 5. 完成！

访问 Netlify 给你生成的网址，你现在的应用就在全世界都能访问了！
