// 1. 设置页面
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 3cm),
  numbering: "1",
)

// 2. 字体配置
// 显式加载刚才上传的 Fandol 字体文件
#set text(
  font: ("Times New Roman", "FandolSong"), 
  size: 12pt,
  lang: "zh"
)

// 配置粗体映射：当使用 *粗体* 时，Typst 会自动使用 Bold 文件
#show strong: set text(font: ("Times New Roman", "FandolSong"), weight: "bold")

// 华文行楷辅助函数 (仅用于封面标题)
#let xingkai(body) = text(font: "STXingkai", size: 36pt, weight: "bold", body)

// 章节标题：使用 FandolSong 的粗体
#show heading: it => [
  #set text(font: ("Times New Roman", "FandolSong"), weight: "bold")
  #block(it)
]

// 3. 辅助函数：封面信息行
#let info_row(label, value, line_width: 7cm) = {
  let label_box = box(width: 5em, align(center)[
    #let chars = label.clusters()
    #if chars.len() == 2 {
      chars.first() + h(1fr) + chars.last()
    } else {
      label
    }
  ])
  
  let value_box = box(
    width: line_width,
    stroke: (bottom: 0.5pt + black),
    outset: (bottom: 2pt), 
    align(center, value)
  )

  block(height: 1.8em)[
    #text(weight: "bold")[#label_box]：#value_box
  ]
}

#let data = json("real_data.json")

// ================= 封面 =================
#align(center)[
  // 如果没有校徽，显示占位文本
  #image("school_logo.png", width: 10cm) 
  
  #v(2.5cm)
  
  // 只有这里使用行楷
  #xingkai[《#data.title》]
  #v(1cm)
  #xingkai[课程论文]
  
  #v(3cm)
  
  #set text(size: 16pt)
  #align(center)[
    #info_row("学院", data.college)
    #info_row("专业", data.major)
    #info_row("年级", data.grade)
    #info_row("学号", data.student_id)
    #info_row("姓名", data.student_name)
    #info_row("指导老师", data.supervisor)
    // 如果有课程名称，也可以显示
    #if "course" in data {
       info_row("课程", data.course)
    }
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

#for block in data.content_blocks {
  if block.type == "section" {
    heading(level: 1, block.title)
    
  } else if block.type == "text" {
    par(justify: true, first-line-indent: 2em)[
      #block.content
    ]
    v(0.5em)
    
  } else if block.type == "equation" {
    align(center)[
      #eval("$ " + block.content + " $")
    ]
    
  } else if block.type == "table" {
    figure(
      table(
        columns: block.headers.len(),
        align: center + horizon,
        stroke: none,
        table.hline(y: 0, stroke: 1.5pt),
        table.header(..block.headers.map(h => [*#h*])),
        table.hline(y: 1, stroke: 0.5pt),
        ..block.rows.flatten(),
        table.hline(stroke: 1.5pt),
      ),
      caption: "数据表"
    )
  }
}
