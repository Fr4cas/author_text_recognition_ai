from pathlib import Path
import json

from docx import Document


BASE_DIR = Path(__file__).resolve().parent

SOURCE_DIR = BASE_DIR / "source" / "transcriptions"
PDF_DIR = BASE_DIR / "source" / "pdf"
OUTPUT_DIR = BASE_DIR / "processed" / "transcriptions"
REGISTRY_PATH = OUTPUT_DIR.parent / "document_registry.json"


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


def load_document_registry(docx_files):
    """Load existing document IDs and assign IDs to new DOCX files."""

    if REGISTRY_PATH.exists():
        with open(REGISTRY_PATH, "r", encoding="utf-8") as file:
            registry = json.load(file)
    else:
        registry = {}

    # Find the next available numeric ID without changing existing assignments.
    existing_numbers = [
        int(document_id[3:])
        for document_id in registry.values()
        if document_id.startswith("DOC") and document_id[3:].isdigit()
    ]
    next_number = max(existing_numbers, default=0) + 1

    # Sorted input makes the initial assignment predictable.
    for docx_path in sorted(docx_files):
        filename = docx_path.name

        if filename not in registry:
            registry[filename] = f"DOC{next_number:03d}"
            next_number += 1

    REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)

    with open(REGISTRY_PATH, "w", encoding="utf-8") as file:
        json.dump(registry, file, ensure_ascii=False, indent=4)

    return registry


def extract_paragraphs(docx_path, document_id):
    """Extract paragraphs while preserving their order and Word styles."""

    document = Document(docx_path)
    paragraphs = []

    for index, paragraph in enumerate(document.paragraphs, start=1):
        text = paragraph.text.strip()

        if not text:
            continue

        paragraphs.append({
            "document_id": document_id,
            "paragraph_id": index,
            "text": text,
            "word_style": paragraph.style.name,
            "classification": "unclassified",
            "page_break_after": has_page_break(paragraph),
        })

    return paragraphs


def process_document(docx_path, document_id):
    docx_path = Path(docx_path)

    pdf_filename = docx_path.stem.replace(
        "文字檔", "掃描檔"
    ) + ".pdf"

    pdf_path = PDF_DIR / pdf_filename

    paragraphs = extract_paragraphs(docx_path, document_id)

    result = {
        "document_id": document_id,
        "document_name": docx_path.stem,
        "source_file": docx_path.name,
        "pdf_file": pdf_filename if pdf_path.exists() else None,
        "paragraph_count": len(paragraphs),
        "paragraphs": paragraphs,
    }

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_path = OUTPUT_DIR / f"{docx_path.stem}.json"

    with open(output_path, "w", encoding="utf-8") as file:
        json.dump(
            result,
            file,
            ensure_ascii=False,
            indent=4,
        )

    print(f"Processed: {docx_path.name}")
    print(f"Document ID: {document_id}")
    print(f"Paragraphs: {len(paragraphs)}")
    print(f"Output: {output_path}")

    return result


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    docx_files = sorted(SOURCE_DIR.glob("*.docx"))

    if not docx_files:
        print(f"No DOCX files found in: {SOURCE_DIR}")
        return

    registry = load_document_registry(docx_files)

    print(f"Found {len(docx_files)} DOCX files.")

    successful = 0
    failed = 0

    for docx_path in docx_files:
        try:
            document_id = registry[docx_path.name]
            process_document(docx_path, document_id)
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
    print(f"ID registry:     {REGISTRY_PATH}")


if __name__ == "__main__":
    main()
