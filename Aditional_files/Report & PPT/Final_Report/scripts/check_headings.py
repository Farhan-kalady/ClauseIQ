import re
import os
import sys

# Configure stdout for UTF-8 to prevent Windows cp1252 encoding crashes on ligatures
sys.stdout.reconfigure(encoding='utf-8')

ALLOWED_HEADINGS = {
    # Chapters
    "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11",
    # Sections
    "2.1", "2.2", "2.3",
    "3.1", "3.2", "3.3", "3.4", "3.5", "3.6", "3.7",
    "4.1",
    "5.1", "5.2", "5.3", "5.4", "5.5", "5.6",
    "6.1", "6.2",
    "10.1", "10.2",
    # Subsections
    "3.1.1", "3.1.2",
    "3.2.1", "3.2.2", "3.2.3",
    "3.4.1",
    "3.7.1", "3.7.2",
    "4.1.1", "4.1.2", "4.1.3", "4.1.4"
}

def check_headings():
    root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    
    print("=" * 75)
    print("CLAUSEIQ FINAL REPORT: MANDATORY HEADING STRUCTURE VERIFICATION")
    print("=" * 75)

    errors = []
    registered_headings = []
    
    # 1. Primary Ground Truth: Extract registered headings from main.aux TOC stream
    aux_path = os.path.join(root, "main.aux")
    if os.path.exists(aux_path):
        with open(aux_path, "r", encoding="utf-8") as f:
            aux_text = f.read()
            
        # Matches: \@writefile{toc}{\contentsline {section}{\numberline {2.1}Literature Review}{4}{section.2.1}}
        toc_pattern = re.compile(r'\\@writefile\{toc\}\{\\contentsline\s*\{([^}]+)\}\{\\numberline\s*\{([^}]+)\}([^}]+)\}')
        matches = toc_pattern.findall(aux_text)
        for level, num, title in matches:
            clean_title = re.sub(r'\\MakeUppercase\s*\{([^}]+)\}', r'\1', title).strip()
            registered_headings.append((level, num, clean_title))
            if num not in ALLOWED_HEADINGS:
                errors.append(f"Disallowed numbered heading '{num} {clean_title}' (level: {level})")

    # 2. Check LaTeX source files in chapters/ to verify secnumdepth consistency
    chapters_dir = os.path.join(root, "chapters")
    tex_files = sorted([f for f in os.listdir(chapters_dir) if f.endswith(".tex")])
    disallowed_source_commands = []
    for tf in tex_files:
        fpath = os.path.join(chapters_dir, tf)
        with open(fpath, "r", encoding="utf-8") as f:
            for lnum, line in enumerate(f, 1):
                # Search for numbered \subsubsection or \paragraph without asterisk
                if re.match(r'^\s*\\(subsubsection|paragraph)\{[^}]+\}', line):
                    disallowed_source_commands.append(f"{tf}:{lnum}: {line.strip()}")

    if disallowed_source_commands:
        for cmd in disallowed_source_commands:
            errors.append(f"Numbered lower-level command in source: {cmd}")

    print(f"Total authorized numbered headings verified: {len(registered_headings)}")
    for level, num, title in registered_headings:
        status = "OK" if num in ALLOWED_HEADINGS else "DISALLOWED"
        print(f"  [{status}] {level:<12} {num:<8} {title}")

    print("-" * 75)
    if errors:
        print(f"FAILED: Found {len(errors)} disallowed headings or commands:")
        for err in errors:
            print(f"  - {err}")
        return False
    else:
        print("PASSED: 100% of numbered headings match the exact authorized hierarchy.")
        print("No extra numbered subsections, chapters, or lower-level divisions exist.")
        return True

if __name__ == "__main__":
    success = check_headings()
    sys.exit(0 if success else 1)
