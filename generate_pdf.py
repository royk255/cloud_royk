import os
from reportlab.platypus import SimpleDocTemplate, Preformatted, Spacer
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.pagesizes import A4


def build_combined_pdf(py_files, output_file):
    code_style = ParagraphStyle(
        name="CodeStyle",
        fontName="Courier",
        fontSize=9,
        leading=11,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=0,
    )

    header_style = ParagraphStyle(
        name="HeaderStyle",
        fontName="Courier-Bold",
        fontSize=11,
        leading=13,
        leftIndent=0,
        rightIndent=0,
        firstLineIndent=0,
        spaceBefore=0,
        spaceAfter=0,
    )

    doc = SimpleDocTemplate(
        output_file,
        pagesize=A4,
        leftMargin=20,
        rightMargin=20,
        topMargin=20,
        bottomMargin=20,
    )

    story = []

    for index, py_file in enumerate(py_files):
        with open(py_file, "r", encoding="utf-8") as f:
            text = f.read().expandtabs(4)

        header_text = f"{os.path.basename(py_file)}\n======="

        story.append(Preformatted(header_text, header_style))
        story.append(Spacer(1, 8))
        story.append(Preformatted(text, code_style))

        if index != len(py_files) - 1:
            story.append(Spacer(1, 16))

    doc.build(story)


def main():
    current_dir = os.getcwd()
    output_dir = os.path.join(current_dir, "res_pdf_2")
    os.makedirs(output_dir, exist_ok=True)

    py_files = sorted(
        [
            os.path.join(current_dir, f)
            for f in os.listdir(current_dir)
            if f.endswith(".py")
        ]
    )

    if not py_files:
        print("No .py files found in current directory.")
        return

    output_file = os.path.join(output_dir, "combined_python_files.pdf")

    try:
        build_combined_pdf(py_files, output_file)
        print(f"Created combined PDF: {output_file}")
    except Exception as e:
        print(f"Failed to create PDF: {e}")


if __name__ == "__main__":
    main()