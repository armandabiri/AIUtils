import os
import re

def extract_document_content(tex_content):
    """Extracts the content between \\begin{document} and \\end{document}, skipping specified environments."""

    # Lookup table for LaTeX environments to remove
    tags = ['equation','equations','figure','figures','equation\*','table','tabular','subequations','eqnarray','flalign','frame','align','thebibliography']

    # Extract content between \begin{document} and \end{document}
    document_pattern = re.compile(r'\\begin{document}(.*?)\\end{document}', re.DOTALL)
    match = document_pattern.search(tex_content)

    if match:
        document_content = match.group(1)

        # Remove content between \begin{} and \end{} for the specified environments
        for tag in tags:
            environment_pattern = re.compile(rf'\\begin\{{{tag}\}}.*?\\end\{{{tag}\}}', re.DOTALL)
            document_content = re.sub(environment_pattern, '', document_content)

         # Remove content between \[ and \]
        document_content = re.sub(r'\\\[.*?\\\]', '', document_content, flags=re.DOTALL)

         # Remove content between $$ and $$
        document_content = re.sub(r'\$\$.*?\$\$', '', document_content, flags=re.DOTALL)


        # Remove lines that start with %, \include, or \input, and also remove empty lines
        document_content = '\n'.join(
            line for line in document_content.splitlines()
            if line.strip() and not (
                line.strip().startswith('%') or
                line.strip().startswith('\\include') or
                line.strip().startswith('\\input')
            )
        )

        return document_content.strip()

    return None


def read_tex_files(directory):
    """Recursively reads all .tex files from the directory and subdirectories."""
    tex_contents = []

    # Walk through all subdirectories and files in the directory
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.tex'):
                print(f"Reading {file}...")
                file_path = os.path.join(root, file)
                # Try reading the file with UTF-8 and fall back to latin-1 if there's an error
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        tex_content = f.read()
                except UnicodeDecodeError:
                    with open(file_path, 'r', encoding='latin-1') as f:
                        tex_content = f.read()

                # Extract content between \begin{document} and \end{document}
                extracted_content = extract_document_content(tex_content)
                if extracted_content:
                    tex_contents.append(extracted_content)

    return tex_contents

def save_to_text_file(contents, output_file_base, max_chars_per_file=1_000_000):
    """Saves the extracted contents to text files, with each file limited to max_chars_per_file characters."""
    # Join all the content into one large string
    all_content = '\n'.join(contents)

    # Split the content into chunks of max_chars_per_file
    for i in range(0, len(all_content), max_chars_per_file):
        chunk = all_content[i:i + max_chars_per_file]
        output_file = f"{output_file_base}_{i // max_chars_per_file + 1}.txt"

        # Write the chunk to a new file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(chunk)


if __name__ == "__main__":
    folder_path = 'C:/Users/adabiri/OneDrive/WorkStations/Research/Papers/@Published'  # Replace with the path to your folder
    output_file_base  = 'output/my_papers'

    # Ensure the output directory exists
    output_dir = os.path.dirname(output_file_base)
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Open the first file to erase its contents at the start (if it exists)
    with open(f'{output_file_base}_1.txt', 'w', encoding='utf-8'):
        pass  # This will erase the contents of the first file

    # Read .tex files and extract content
    tex_contents = read_tex_files(folder_path)

    # Save extracted content to text files, limited to 1e6 characters per file
    save_to_text_file(tex_contents, output_file_base, max_chars_per_file=int(1e6))

    print(f"Extracted content from .tex files has been saved to files starting with '{output_file_base}_'.")
