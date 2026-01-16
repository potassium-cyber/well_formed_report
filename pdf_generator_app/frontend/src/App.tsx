import { useState } from 'react'
import './App.css'
import axios from 'axios'



// 定义内容块类型
interface ContentBlock {
  id: string;
  type: 'section' | 'text' | 'equation' | 'table';
  title?: string;
  content?: string;
  headers?: string[];
  rows?: string[][];
}

function App() {
  const [formData, setFormData] = useState({
    course: "创新创造能力训练I", // 默认课程
    title: "基于深度学习的图像识别研究",
    student_name: "张小明",
    student_id: "20230001",
    college: "计算机科学与工程学院",
    major: "软件工程",
    grade: "2023级",
    supervisor: "李教授",
  });

  // 动态内容块状态
  const [blocks, setBlocks] = useState<ContentBlock[]>([
    { id: '1', type: 'section', title: '引言' },
    { id: '2', type: 'text', content: '随着人工智能技术的飞速发展，计算机视觉已成为最热门的研究领域之一。' }
  ]);

  const [loading, setLoading] = useState(false);
  const [pdfUrl, setPdfUrl] = useState<string | null>(null);

  // 添加内容块
  const addBlock = (type: ContentBlock['type']) => {
    const newBlock: ContentBlock = {
      id: Math.random().toString(36).substr(2, 9),
      type,
      ...(type === 'section' ? { title: '新章节' } : {}),
      ...(type === 'text' ? { content: '' } : {}),
      ...(type === 'equation' ? { content: 'E = m c^2' } : {}),
      ...(type === 'table' ? { 
        headers: ['列1', '列2'], 
        rows: [['数据1', '数据2'], ['数据3', '数据4']] 
      } : {}),
    };
    setBlocks([...blocks, newBlock]);
  };

  // 更新内容块内容
  const updateBlock = (id: string, field: string, value: any) => {
    setBlocks(blocks.map(b => b.id === id ? { ...b, [field]: value } : b));
  };

  // 删除内容块
  const removeBlock = (id: string) => {
    setBlocks(blocks.filter(b => b.id !== id));
  };

  const handleGenerate = async () => {
    setLoading(true);
    try {
      const payload = {
        ...formData,
        title_en: "Research on Image Recognition",
        supervisor_en: "Prof. Li",
        student_name_en: "Xiaoming Zhang",
        finish_year: "2026",
        finish_month: "6",
        abstract_zh: "摘要内容...",
        keywords_zh: "关键词",
        abstract_en: "Abstract...",
        keywords_en: "Keywords",
        content_blocks: blocks // 使用动态生成的块
      };

      // 确定 API 地址：优先使用环境变量（生产环境），否则使用代理路径（本地开发）
      const apiUrl = import.meta.env.VITE_API_URL || '/api';
      
      // 发送请求
      const response = await axios.post(`${apiUrl}/generate`, payload, {
        responseType: 'blob' // 关键！告诉 axios 返回的是二进制文件流
      });
      const url = window.URL.createObjectURL(new Blob([response.data], { type: 'application/pdf' }));
      setPdfUrl(url);
    } catch (error) {
      alert("生成失败");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', height: '100vh', fontFamily: 'sans-serif' }}>
      {/* 左侧：编辑器 */}
      <div style={{ width: '500px', padding: '20px', borderRight: '1px solid #ddd', overflowY: 'auto' }}>
        <h2 style={{ borderBottom: '2px solid #007bff', paddingBottom: '10px' }}>🎓 报告编辑器</h2>
        
        {/* 1. 基础信息 */}
        <section style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666' }}>基础信息</h3>
          
          <div className="form-group">
            <label>选择课程</label>
            <select 
              name="course" 
              value={formData.course} 
              onChange={(e) => setFormData({...formData, course: e.target.value})}
              style={{ width: '100%', padding: '8px', border: '1px solid #ddd', borderRadius: '4px' }}
            >
              <option value="创新创造能力训练I">创新创造能力训练I</option>
              <option value="创新创造能力训练II">创新创造能力训练II</option>
              <option value="教育见习">教育见习</option>
              <option value="人工智能导论">人工智能导论</option>
            </select>
          </div>

          <div className="form-group">
            <label>论文标题</label>
            <input name="title" value={formData.title} onChange={(e) => setFormData({...formData, title: e.target.value})} />
          </div>
          <div style={{ display: 'flex', gap: '10px' }}>
            <div className="form-group" style={{ flex: 1 }}>
              <label>姓名</label>
              <input value={formData.student_name} onChange={(e) => setFormData({...formData, student_name: e.target.value})} />
            </div>
            <div className="form-group" style={{ flex: 1 }}>
              <label>学号</label>
              <input value={formData.student_id} onChange={(e) => setFormData({...formData, student_id: e.target.value})} />
            </div>
          </div>
        </section>

        {/* 2. 动态内容块 */}
        <section style={{ marginBottom: '30px' }}>
          <h3 style={{ color: '#666' }}>正文内容</h3>
          {blocks.map((block) => (
            <div key={block.id} style={{ 
              border: '1px solid #eee', 
              padding: '15px', 
              marginBottom: '15px', 
              borderRadius: '8px',
              position: 'relative',
              backgroundColor: '#fff'
            }}>
              <span style={{ fontSize: '12px', color: '#aaa', position: 'absolute', top: '5px', right: '10px' }}>
                {block.type.toUpperCase()}
              </span>

              {block.type === 'section' && (
                <input 
                  style={{ fontSize: '18pt', fontWeight: 'bold', width: '100%', border: 'none', borderBottom: '1px solid #eee' }}
                  value={block.title} 
                  onChange={(e) => updateBlock(block.id, 'title', e.target.value)}
                  placeholder="请输入章节标题..."
                />
              )}

              {block.type === 'text' && (
                <textarea 
                  style={{ width: '100%', minHeight: '80px', border: '1px solid #f0f0f0', borderRadius: '4px', padding: '5px' }}
                  value={block.content} 
                  onChange={(e) => updateBlock(block.id, 'content', e.target.value)}
                  placeholder="请输入正文内容..."
                />
              )}

              {block.type === 'equation' && (
                <div style={{ backgroundColor: '#f8f9fa', padding: '10px', borderRadius: '4px' }}>
                  <label style={{ fontSize: '12px', color: '#666' }}>LaTeX 公式代码:</label>
                  <input 
                    style={{ width: '100%', fontFamily: 'monospace', marginTop: '5px' }}
                    value={block.content} 
                    onChange={(e) => updateBlock(block.id, 'content', e.target.value)}
                  />
                </div>
              )}

              {block.type === 'table' && (
                <div style={{ overflowX: 'auto' }}>
                  <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: '12px' }}>
                    <thead>
                      <tr>
                        {block.headers?.map((h, i) => (
                          <th key={i}>
                            <input 
                              style={{ width: '60px', fontWeight: 'bold' }} 
                              value={h} 
                              onChange={(e) => {
                                const newHeaders = [...(block.headers || [])];
                                newHeaders[i] = e.target.value;
                                updateBlock(block.id, 'headers', newHeaders);
                              }}
                            />
                          </th>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {block.rows?.map((row, rowIndex) => (
                        <tr key={rowIndex}>
                          {row.map((cell, colIndex) => (
                            <td key={colIndex}>
                              <input 
                                style={{ width: '60px' }} 
                                value={cell} 
                                onChange={(e) => {
                                  const newRows = [...(block.rows || [])];
                                  newRows[rowIndex][colIndex] = e.target.value;
                                  updateBlock(block.id, 'rows', newRows);
                                }}
                              />
                            </td>
                          ))}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  <button style={{ fontSize: '10px', marginTop: '5px' }} onClick={() => {
                    const newRows = [...(block.rows || []), new Array(block.headers?.length).fill('')];
                    updateBlock(block.id, 'rows', newRows);
                  }}>+ 添加行</button>
                </div>
              )}

              <button 
                onClick={() => removeBlock(block.id)}
                style={{ marginTop: '10px', color: 'red', fontSize: '12px', border: 'none', background: 'none', cursor: 'pointer' }}
              >
                🗑 删除块
              </button>
            </div>
          ))}

          {/* 工具栏 */}
          <div style={{ display: 'flex', gap: '10px', marginTop: '20px' }}>
            <button className="add-btn" onClick={() => addBlock('section')}>+ 章节</button>
            <button className="add-btn" onClick={() => addBlock('text')}>+ 段落</button>
            <button className="add-btn" onClick={() => addBlock('equation')}>+ 公式</button>
            <button className="add-btn" onClick={() => addBlock('table')}>+ 表格</button>
          </div>
        </section>

        <button 
          onClick={handleGenerate} 
          disabled={loading}
          style={{ 
            marginTop: '40px', 
            width: '100%', 
            padding: '15px',
            backgroundColor: loading ? '#ccc' : '#28a745',
            color: 'white',
            fontWeight: 'bold',
            fontSize: '16px',
            border: 'none',
            borderRadius: '8px',
            cursor: loading ? 'not-allowed' : 'pointer',
            boxShadow: '0 4px 6px rgba(0,0,0,0.1)'
          }}
        >
          {loading ? '正在排版中...' : '🚀 生成 PDF 报告'}
        </button>
      </div>

      {/* 右侧：预览 */}
      <div style={{ flex: 1, backgroundColor: '#525659', display: 'flex', flexDirection: 'column' }}>
        <div style={{ padding: '10px', backgroundColor: '#333', color: '#fff', textAlign: 'center', fontSize: '14px' }}>
          实时预览
        </div>
        {pdfUrl ? (
          <iframe src={pdfUrl} style={{ width: '100%', height: '100%', border: 'none' }} title="Preview" />
        ) : (
          <div style={{ flex: 1, display: 'flex', justifyContent: 'center', alignItems: 'center', color: '#ccc' }}>
            请填写内容并点击生成按钮查看结果
          </div>
        )}
      </div>
    </div>
  )
}

export default App
