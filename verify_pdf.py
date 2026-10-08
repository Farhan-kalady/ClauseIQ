import fitz

pdf_path = r'reports/interim_report/main.pdf'
doc = fitz.open(pdf_path)
print('Total pages:', len(doc))
print('\nTOC entries count:', len(doc.get_toc()))
for item in doc.get_toc():
    print(item)

print('\nHeader/Footer Analysis across pages:')
for i in range(len(doc)):
    page = doc[i]
    text = page.get_text('text')
    lines = [l.strip() for l in text.split('\n') if l.strip()]
    first_line = lines[0] if lines else ''
    last_line = lines[-1] if lines else ''
    # Check for page numbers
    print(f'Page {i+1}: First line: "{first_line[:45]}" | Last line: "{last_line}"')
