// 1. 设置页面
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 3cm),
  numbering: "1",
)

// 2. 字体设置
#set text(
  font: ("Times New Roman", "Songti SC", "SimSun"),
  size: 12pt,
  lang: "zh"
)

// 华文行楷辅助函数
#let xingkai(body) = text(font: "STXingkai", weight: "bold", size: 36pt, body)

// 3. 辅助函数：封面信息行
// label: 标签文本（如"学院"）
// value: 填入的内容
// width: 下划线的总长度
#let info_row(label, value, line_width: 7cm) = {
  // 左侧标签：固定宽度，分散对齐
  let label_box = box(width: 5em, align(center)[
    #let chars = label.clusters()
    #if chars.len() == 2 {
      // 两个字：中间加很多空格
      chars.first() + h(1fr) + chars.last()
    } else {
      label
    }
  ])
  
  // 右侧内容：下划线盒子
  let value_box = box(
    width: line_width,
    stroke: (bottom: 0.5pt + black),
    outset: (bottom: 2pt), // 下划线稍微往下一点
    align(center, value)
  )

  // 组合
  block(height: 1.8em)[
    #text(weight: "bold")[#label_box]：#value_box
  ]
}

// 读取数据
#let data = json("real_data.json")

// ================= 封面 =================
#align(center)[
  #image("school_logo.png", width: 10cm)
  #v(2.5cm)
  
  #xingkai[《#data.title》]
  #v(1cm)
  #xingkai[课程论文]
  
  #v(3cm)
  
  // 信息表区域
  #set text(size: 16pt)
  #align(center)[
    #info_row("学院", data.college)
    #info_row("专业", data.major)
    #info_row("年级", data.grade)
    #info_row("学号", data.student_id)
    #info_row("姓名", data.student_name)
    #info_row("指导老师", data.supervisor)
  ]
  
  #v(1fr)
  
  #text(size: 14pt)[
    完成日期： 
    #box(width: 1.5cm, stroke: (bottom: 0.5pt), align(center, data.finish_year)) 年 
    #box(width: 1cm, stroke: (bottom: 0.5pt), align(center, data.finish_month)) 月
  ]
]

// ================= 摘要 =================
#pagebreak()
#set page(numbering: "i")
#counter(page).update(1)

#align(center)[
  #text(size: 16pt, weight: "bold")[#data.title]
  #v(0.5em)
  #text(size: 14pt)[#data.student_name \quad 指导老师：#data.supervisor]
]

#v(1em)
#align(center)[#text(size: 16pt, weight: "bold")[摘 要]]
#v(0.5em)

#par(justify: true, first-line-indent: 2em)[
  #data.abstract_zh
]

#v(1em)
*关键词：* #data.keywords_zh

#pagebreak()
#align(center)[
  #text(size: 16pt, weight: "bold")[#data.title_en]
  #v(0.5em)
  #text(size: 14pt)[#data.student_name_en \quad Supervisor: #data.supervisor_en]
]

#v(1em)
#align(center)[#text(size: 16pt, weight: "bold")[Abstract]]
#v(0.5em)

#par(justify: true)[
  #data.abstract_en
]

#v(1em)
*Keywords:* #data.keywords_en

// ================= 目录 =================
#pagebreak()
#outline(title: "目录", indent: auto)

// ================= 正文 =================
#pagebreak()
#set page(numbering: "1")
#counter(page).update(1)

// 动态渲染
#for block in data.content_blocks {
  if block.type == "section" {
    heading(level: 1, block.title)
    
  } else if block.type == "text" {
    par(justify: true, first-line-indent: 2em)[
      #block.content
    ]
    v(0.5em)
    
  } else if block.type == "equation" {
    // 渲染数学公式
    // block.content 是纯文本 "E=mc^2"，我们需要把它变成 Typst 的 math block
    // eval 动态执行代码： $ + content + $
    align(center)[
      #eval("$ " + block.content + " $")
    ]
    
  } else if block.type == "table" {
    figure(
      table(
        columns: block.headers.len(),
        align: center + horizon,
        stroke: none, // 去掉默认网格线
        
        // 三线表：顶线
        table.hline(y: 0, stroke: 1.5pt),
        // 表头
        table.header(..block.headers.map(h => [*#h*])),
        // 表头下的线
        table.hline(y: 1, stroke: 0.5pt),
        
        // 内容
        ..block.rows.flatten(),
        
        // 底线
        table.hline(stroke: 1.5pt),
      ),
      caption: "数据表"
    )
  }
}