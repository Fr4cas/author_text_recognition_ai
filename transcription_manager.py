from pathlib import Path
import json
from docx import Document


BASE_DIR = Path(__file__).resolve().parent

SOURCE_DIR = BASE_DIR / "source" / "transcriptions"
OUTPUT_DIR = BASE_DIR / "processed" / "transcriptions"


def has_page_break(paragraph):
    """Check whether a paragraph contains an explicit page break."""

    for run in paragraph.runs:
        for element in run._element:
            if element.tag.endswith("}br"):
                if element.get(
                    "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}type"
                ) == "page":
                    return True

    return False


def extract_paragraphs(docx_path):
    """Extract paragraphs while preserving their order and styles."""

    document = Document(docx_path)

    paragraphs = []

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = paragraph.text.strip()

        if not text:
            continue

        paragraphs.append({
            "paragraph_id": index,
            "text": text,
            "style": paragraph.style.name,
            "page_break_after": has_page_break(paragraph)
        })

    return paragraphs


def process_document(docx_path):
    docx_path = Path(docx_path)

    paragraphs = extract_paragraphs(docx_path)

    result = {
        "document_name": docx_path.stem,
        "source_file": docx_path.name,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{docx_path.stem}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4
        )

    print(f"Processed: {docx_path.name}")
    print(f"Paragraphs: {len(paragraphs)}")
    print(f"Output: {output_path}")

    return result


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    docx_files = sorted(SOURCE_DIR.glob("*.docx"))

    if not docx_files:
        print(f"No DOCX files found in: {SOURCE_DIR}")
        return

    print(f"Found {len(docx_files)} DOCX files.")

    successful = 0
    failed = 0

    for docx_path in docx_files:
        try:
            process_document(docx_path)
            successful += 1

        except Exception as error:
            failed += 1
            print(f"ERROR processing {docx_path.name}: {error}")

    print("\n" + "=" * 40)
    print("TRANSCRIPTION SUMMARY")
    print("=" * 40)
    print(f"Documents found: {len(docx_files)}")
    print(f"Successful:      {successful}")
    print(f"Failed:          {failed}")


if __name__ == "__main__":
    main()
