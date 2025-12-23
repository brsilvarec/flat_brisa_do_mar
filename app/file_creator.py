import pypandoc
import os

def docx_to_html(docx_path):
    """
    Convert a DOCX file to HTML string using pypandoc.
    
    Args:
        docx_path (str): Path to the input DOCX file
    
    Returns:
        str: HTML content as string
    
    Raises:
        FileNotFoundError: If the input DOCX file doesn't exist
        RuntimeError: If pypandoc conversion fails
    """
    # Check if input file exists
    if not os.path.exists(docx_path):
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")
    
    try:
        # Convert DOCX to HTML and return as string
        html_content = pypandoc.convert_file(docx_path, 'html')
        return html_content
    
    except Exception as e:
        raise RuntimeError(f"Conversion failed: {e}") from e

# Example usage
if __name__ == "__main__":
    try:
        html_string = docx_to_html("data/template.docx")
        print("HTML Content:")
        print(html_string)
        
    except Exception as e:
        print(f"Error: {e}")