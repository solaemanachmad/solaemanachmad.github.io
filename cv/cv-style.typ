// Gaya tambahan untuk versi PDF (Typst)
#let accent = rgb("#0B2545")   // UGM navy
#let gold = rgb("#C99A2E")     // UGM gold
#let muted = rgb("#5c6b73")

#set par(justify: false, leading: 0.55em)
#set list(indent: 0.4em, body-indent: 0.5em)
#show link: set text(fill: rgb("#163A67"))

// Section heading: uppercase with a rule underneath
#show heading.where(level: 1): it => block(above: 1.3em, below: 0.6em)[
  #set text(font: ("Segoe UI", "Source Sans 3"), size: 11.5pt, weight: "bold", fill: accent, tracking: 0.06em)
  #upper(it.body)
  #v(-0.65em)
  #line(length: 100%, stroke: 1.2pt + gold)
]

// Entry title
#show heading.where(level: 2): it => block(above: 0.9em, below: 0.35em)[
  #set text(font: ("Segoe UI", "Source Sans 3"), size: 10.5pt, weight: "semibold", fill: black)
  #it.body
]

