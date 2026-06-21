from tinydb import TinyDB
from pathlib import Path

def gallery(image_path):
    DB_FILE = Path(image_path).parent / "hairlineResults.json"
    OUTPUT_TEX = "gallery.tex"
    IMAGE_DIR = Path(image_path)

    IMAGES_PER_ROW = 3
    IMAGE_HEIGHT = "5cm"

    db = TinyDB(DB_FILE)

    entries = sorted(db.all(), key=lambda x: x["filename"])

    def latex_escape(s):
        return (
            str(s)
            .replace("\\", "\\textbackslash{}")
            .replace("_", "\\_")
            .replace("&", "\\&")
            .replace("%", "\\%")
            .replace("#", "\\#")
            .replace("{", "\\{")
            .replace("}", "\\}")
        )

    with open(OUTPUT_TEX, "w", encoding="utf8") as f:

        f.write(r"""\documentclass[a4paper]{article}
\usepackage[a4paper,margin=1cm]{geometry}
\usepackage{graphicx}
\usepackage{array}
\usepackage{longtable}
\usepackage{float}
\usepackage{grffile}
\usepackage[T1]{fontenc}

\pagestyle{empty}
\setlength{\parindent}{0pt}

\begin{document}

""")

        for i in range(0, len(entries), IMAGES_PER_ROW):

            row = entries[i:i + IMAGES_PER_ROW]

            cols = "c" * len(row)
            f.write(r"\begin{tabular}{" + cols + "}\n")

            #
            # Images
            #
            image_cells = []
            for e in row:
                img_path = Path(IMAGE_DIR) / e["filename"]
                image_cells.append(
                    rf"\includegraphics[height={IMAGE_HEIGHT}]{{{img_path.as_posix()}}}"
                )

            f.write(" & ".join(image_cells) + r"\\[2mm]" + "\n")

            # LaTeX comment with filenames
            f.write("% " + ", ".join(e["filename"] for e in row) + "\n")

            #
            # Text cells (FIXED)
            #
            text_cells = []

            for e in row:

                lines = []

                lines.append(rf"\texttt{{\tiny {latex_escape(e['filename'])}}}")

                for k, v in e.items():
                    if k == "filename":
                        continue

                    if isinstance(v, float):
                        lines.append(f"{latex_escape(k)}: {v:.4f}")
                    else:
                        lines.append(f"{latex_escape(k)}: {latex_escape(v)}")

                cell = (
                    r"\begin{minipage}[t]{4cm}\ttfamily\tiny "
                    + r" \\ ".join(lines)
                    + r" \end{minipage}"
                )

                text_cells.append(cell)

            f.write(" & ".join(text_cells) + r"\\" + "\n")

            f.write(r"\end{tabular}")
            f.write("\n\n\\vspace{5mm}\n\n")

        f.write(r"\end{document}")
