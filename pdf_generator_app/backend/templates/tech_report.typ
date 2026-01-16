// ================= 配置区域 =================
#set page(
  paper: "a4",
  margin: (top: 2.5cm, bottom: 2.5cm, left: 3cm, right: 3cm),
  numbering: none, // 封面无页码
)

// 字体定义
#let songti = ("Times New Roman", "FandolSong")
#let heiti = ("Times New Roman", "FandolHei")
#let xingkai_font = ("STXingkai")

#set text(font: songti, size: 12pt, lang: "zh")
#show strong: set text(font: heiti, weight: "bold")

// 标题样式
#show heading: it => [
  #set text(font: heiti, weight: "bold")
  #v(0.5em)
  #it
  #v(0.5em)
]

// 辅助函数
#let xingkai(body) = text(font: xingkai_font, size: 36pt, weight: "bold", body)
#let bold_label(body) = text(font: heiti, weight: "bold", body)

#let info_row(label, value, line_width: 7cm) = {
  let label_box = box(width: 5em, align(center)[
    #bold_label[
      #let chars = label.clusters()
      #if chars.len() == 2 {
        chars.first() + h(1fr) + chars.last()
      } else {
        label
      }
    ]
  ])
  let value_box = box(
    width: line_width,
    stroke: (bottom: 0.5pt + black),
    outset: (bottom: 2pt), 
    align(center, value)
  )
  block(height: 1.8em)[#label_box：#value_box]
}

#let data = json("real_data.json")

// ================= 封面 (单页) =================
// 使用 grid 或 stack 布局来强制控制在一页内
#align(center + horizon)[ 
  #v(-2cm) // 稍微往上提一点
  #image("school_logo.png", width: 10cm) 
  
  #v(2fr) // 弹性间距
  
  #xingkai[《#data.title》]
  #v(1cm)
  #xingkai[课程论文]
  
  #v(3fr) // 弹性间距
  
  #set text(size: 16pt)
  #align(center)[
    #info_row("学院", data.college)
    #info_row("专业", data.major)
    #info_row("年级", data.grade)
    #info_row("学号", data.student_id)
    #info_row("姓名", data.student_name)
    #info_row("指导老师", data.supervisor)
    #if "course" in data {
       info_row("课程", data.course)
    }
  ]
  
  #v(2fr)
  
  #text(size: 14pt)[
    完成日期： 
    #box(width: 1.5cm, stroke: (bottom: 0.5pt), align(center, data.finish_year)) 年 
    #box(width: 1cm, stroke: (bottom: 0.5pt), align(center, data.finish_month)) 月
  ]
  #v(1cm)
]

// ================= 摘要 (罗马页码) =================
#pagebreak()
#set page(numbering: "I") // 罗马数字大写 I, II
#counter(page).update(1)

#align(center)[
  #text(size: 16pt, font: heiti, weight: "bold")[#data.title]
  #v(1em)
  // 修复 \quad 为 #h(2em)
  #text(size: 14pt)[#data.student_name #h(2em) 指导老师：#data.supervisor]
]

#v(2em)
#align(center)[#text(size: 16pt, font: heiti, weight: "bold")[摘 要]]
#v(1em)

#par(justify: true, first-line-indent: 2em, leading: 1em)[
  #data.abstract_zh
]

#v(2em)
#bold_label[关键词：] #data.keywords_zh

// ================= 目录 =================
#pagebreak()
#outline(title: text(font: heiti, "目录"), indent: auto)

// ================= 正文 (阿拉伯页码) =================
#pagebreak()
#set page(numbering: "1")
#counter(page).update(1)

#for block in data.content_blocks {
  if block.type == "section" {
    heading(level: 1, block.title)
  } else if block.type == "text" {
    par(justify: true, first-line-indent: 2em, leading: 1em)[
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
        table.header(..block.headers.map(h => [#bold_label[#h]])),
        table.hline(y: 1, stroke: 0.5pt),
        ..block.rows.flatten(),
        table.hline(stroke: 1.5pt),
      ),
      caption: text(font: heiti, "数据表")
    )
  }
}
