import os
import pyperclip
import argparse

def is_text_file(filename):
    text_file_extensions = ['.txt', '.md', '.py', '.html', '.css', '.js', '.json', '.xml', '.csv']
    return any(filename.endswith(ext) for ext in text_file_extensions)

def copy_directory_contents_to_clipboard(dir_path):
    clipboard_content = ""
    for root, dirs, files in os.walk(dir_path):
        for file in files:
            if is_text_file(file):
                file_path = os.path.join(root, file)
                clipboard_content += f"\n\n--- {file_path} ---\n\n"
                try:
                    with open(file_path, 'r') as file:
                        clipboard_content += file.read()
                except Exception as e:
                    clipboard_content += f"Error reading file: {e}\n"

    pyperclip.copy(clipboard_content)
    print("Contents copied to clipboard.")

def main():
    parser = argparse.ArgumentParser(description="Copy contents of a directory to the clipboard.")
    parser.add_argument("directory", help="Path of the directory to copy")
    args = parser.parse_args()
    
    copy_directory_contents_to_clipboard(args.directory)

if __name__ == "__main__":
    main()
