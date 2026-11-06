
from pathlib import Path
import pymupdf


BASE_DIR = Path(__file__).resolve().parent
SOURCE_DIR = BASE_DIR / "source"
OUTPUT_DIR = BASE_DIR / "processed" / "pages"

DPI = 300


def extract_pdf(pdf_path):
    document_name = pdf_path.stem
    document_output = OUTPUT_DIR / document_name

    document_output.mkdir(parents=True, exist_ok=True)

    with pymupdf.open(pdf_path) as document:
        total_pages = len(document)

        print(f"\nProcessing: {pdf_path.name}")
        print(f"Pages: {total_pages}")

        for index, page in enumerate(document, start=1):
            pix = page.get_pixmap(
                dpi=DPI,
                colorspace=pymupdf.csRGB,
                alpha=False
            )

            output_path = document_output / f"page_{index:04d}.png"
            pix.save(output_path)

            print(f"  Saved: {output_path.name}")

    return total_pages


def main():
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)

    pdf_files = sorted(SOURCE_DIR.glob("*.pdf"))

    if not pdf_files:
        print(f"No PDF files found in: {SOURCE_DIR}")
        return

    print(f"Found {len(pdf_files)} PDF files.")

    successful = 0
    failed = 0
    total_pages = 0

    for pdf_path in pdf_files:
        try:
            pages = extract_pdf(pdf_path)

            successful += 1
            total_pages += pages

        except Exception as error:
            failed += 1
            print(f"\nERROR processing {pdf_path.name}: {error}")

    print("\n" + "=" * 40)
    print("EXTRACTION SUMMARY")
    print("=" * 40)
    print(f"Documents found: {len(pdf_files)}")
    print(f"Successful:      {successful}")
    print(f"Failed:          {failed}")
    print(f"Total pages:     {total_pages}")


if __name__ == "__main__":
    main()
