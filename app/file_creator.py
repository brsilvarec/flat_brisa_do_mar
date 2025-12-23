import os
from datetime import datetime
import pypandoc
import logging
from pydantic import BaseModel, Field, ValidationError
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class MappedItems(BaseModel):
    title: str = Field(..., description="Title of the document")
    guest: str = Field(..., description="Guest name")
    nights: str = Field(..., description="Number of nights")
    start: str = Field(..., description="Start date")
    end: str = Field(..., description="End date")
    cond_name: str = Field(..., description="Condominium name")
    flat_number: str = Field(..., description="Flat/apartment number")
    gmaps_list: str = Field(..., description="Google Maps link")
    pass_cond: str = Field(..., description="Condominium password")
    pass_flat: str = Field(..., description="Flat password")
    insta_account: str = Field(..., description="Instagram account")

def load_config(config_path: str) -> MappedItems:
    """
    Load configuration from JSON file. File must exist.

    Args:
        config_path (str): Path to the JSON configuration file

    Returns:
        MappedItems: Instance created from JSON data

    Raises:
        FileNotFoundError: If the JSON file doesn't exist
        ValidationError: If the JSON data is invalid
    """
    if not os.path.exists(config_path):
        logger.error(f"Configuration file not found: {config_path}")
        raise FileNotFoundError(f"Configuration file is required: {config_path}")

    logger.info(f"Loading configuration from {config_path}")

    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            json_data = file.read()

        mapped_data = MappedItems.model_validate_json(json_data)
        logger.info("Configuration loaded and validated successfully")
        return mapped_data

    except ValidationError as e:
        logger.error(f"Invalid configuration data: {e}")
        raise
    except Exception as e:
        logger.error(f"Failed to load configuration file: {e}")
        raise

# Create a function to override guest, start and end dates
def override_config(mapped_items: MappedItems, guest: str = None, start: str = None, end: str = None) -> MappedItems:
    """
    Override specific fields in MappedItems.

    Args:
        mapped_items (MappedItems): Original configuration data
        guest (str, optional): New guest name
        start (str, optional): New start date
        end (str, optional): New end date
    Returns:
        MappedItems: Updated configuration data
    """
    updated_data = mapped_items.model_dump()

    if guest:
        updated_data['guest'] = guest
        logger.info(f"Overriding guest name to: {guest}")
    if start:
        updated_data['start'] = start
        logger.info(f"Overriding start date to: {start}")
    if end:
        updated_data['end'] = end
        logger.info(f"Overriding end date to: {end}")
    
    # Overwrite nights based on new start and end dates if both are provided
    if start and end:
        start_date = datetime.strptime(start, "%Y-%m-%d")
        end_date = datetime.strptime(end, "%Y-%m-%d")
        nights = (end_date - start_date).days
        updated_data['nights'] = str(nights)
        logger.info(f"Updated nights to: {nights}")

    return MappedItems.model_validate(updated_data)

def docx_to_html(docx_path: str) -> str:
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
    logger.info(f"Starting conversion of DOCX file: {docx_path}")

    # Check if input file exists
    if not os.path.exists(docx_path):
        logger.error(f"DOCX file not found: {docx_path}")
        raise FileNotFoundError(f"DOCX file not found: {docx_path}")

    try:
        # Convert DOCX to HTML with image extraction
        extra_args = ['--extract-media', 'media']
        html_content = pypandoc.convert_file(
            docx_path,
            'html',
            extra_args=extra_args
        )
        logger.info("DOCX to HTML conversion completed successfully")
        logger.info("Images extracted to 'media' directory")
        return html_content

    except Exception as e:
        logger.error(f"Conversion failed: {e}")
        raise RuntimeError(f"Conversion failed: {e}") from e

def replace_placeholders(html_content: str, mapped_items: MappedItems) -> str:
    """
    Replace placeholders in HTML content with actual values.

    Args:
        html_content (str): The HTML content containing placeholders
        mapped_items (MappedItems): Object containing the replacement values

    Returns:
        str: HTML content with placeholders replaced
    """
    logger.info("Starting placeholder replacement")

    # Convert to dict for easy iteration
    replacements = {
        f'&lt;{field}&gt;': getattr(mapped_items, field)
        for field in mapped_items.model_dump()
    }

    result = html_content
    replacements_made = 0
    for placeholder, value in replacements.items():
        if placeholder in result:
            result = result.replace(placeholder, value)
            replacements_made += 1
            logger.info(f"Replaced {placeholder} with {value}")

    logger.info(f"Placeholder replacement completed. Made {replacements_made} replacements.")
    return result

def html_to_docx(html_content: str, output_path: str, template_path: str = None) -> None:
    """
    Convert HTML content back to DOCX file using pypandoc, preserving images.

    Args:
        html_content (str): The processed HTML content
        output_path (str): Path where to save the output DOCX file
        template_path (str, optional): Path to original DOCX template for styling

    Raises:
        RuntimeError: If conversion fails
        FileNotFoundError: If template file doesn't exist (when provided)
    """
    logger.info(f"Starting HTML to DOCX conversion: {output_path}")

    # Ensure output directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir and not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Created output directory: {output_dir}")

    try:
        # Prepare extra arguments for pypandoc
        extra_args = []

        # Use template if provided for consistent styling and structure
        if template_path:
            if not os.path.exists(template_path):
                logger.error(f"Template file not found: {template_path}")
                raise FileNotFoundError(f"Template file not found: {template_path}")

            # Use reference document to preserve formatting, styles, and images
            extra_args.extend(['--reference-doc', template_path])
            logger.info(f"Using template for styling and image preservation: {template_path}")

        # Add resource path for images
        if os.path.exists('media'):
            extra_args.extend(['--resource-path', 'media'])
            logger.info("Using media directory for image resources")

        # Convert HTML to DOCX
        pypandoc.convert_text(
            html_content,
            'docx',
            format='html',
            outputfile=output_path,
            extra_args=extra_args
        )

        logger.info(f"HTML to DOCX conversion completed successfully: {output_path}")
        logger.info("Images have been preserved in the output document")

    except Exception as e:
        logger.error(f"HTML to DOCX conversion failed: {e}")
        raise RuntimeError(f"HTML to DOCX conversion failed: {e}") from e

def generate_output_filename(template_path: str, mapped_items: MappedItems) -> str:
    """
    Generate output filename by appending guest suffix and start date to template name.

    Args:
        template_path (str): Path to the original template file
        mapped_items (MappedItems): Configuration data

    Returns:
        str: Generated output file path
    """
    # Get template path components
    template_dir = os.path.dirname(template_path)
    template_name = Path(template_path).stem

    # Create safe guest name for filename
    safe_guest = "".join(c for c in mapped_items.guest if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_guest = safe_guest.replace(' ', '_')

    # Generate filename: template_name_guest_startdate.docx
    filename = f"{template_name}_{safe_guest}_{mapped_items.start}.docx"

    return os.path.join(template_dir, filename)

def convert_docx_with_config(config_map: MappedItems, template_path: str, output_path: str) -> None:
    """
    Convert DOCX template to output DOCX using configuration from JSON file.

    Args:
        config_map (MappedItems): Configuration data
        template_path (str): Path to the DOCX template file
        output_path (str): Path where to save the output DOCX file

    Raises:
        RuntimeError: If any conversion step fails
    """
    try:
        # Convert DOCX to HTML
        html_string = docx_to_html(template_path)

        # Replace placeholders
        final_html = replace_placeholders(html_string, config_map)

        # Convert processed HTML back to DOCX
        html_to_docx(final_html, output_path, template_path)

        logger.info("Document conversion completed successfully")

    except Exception as e:
        logger.error(f"Document conversion failed: {e}")
        raise RuntimeError(f"Document conversion failed: {e}") from e

def main():
    try:
        # Enforce existing JSON configuration file
        config_path = "data/config.json"
        template_path = "data/template.docx"

        # Load configuration
        mapped_data = load_config(config_path)

        # Convert DOCX to HTML (extracts images to media folder)
        html_string = docx_to_html(template_path)

        # Replace placeholders
        final_html = replace_placeholders(html_string, mapped_data)

        # Generate output filename with guest suffix and start date
        output_path = generate_output_filename(template_path, mapped_data)

        # Convert processed HTML back to DOCX using original template as reference
        html_to_docx(final_html, output_path, template_path)

        logger.info("Process completed successfully")
        logger.info(f"Output file saved as: {output_path}")
    except FileNotFoundError as e:
        logger.error(f"Required file missing: {e}")
        logger.error("Please create the required files before running the script")
    except ValidationError as e:
        logger.error(f"Configuration validation failed: {e}")
    except Exception as e:
        logger.error(f"Error: {e}")


# Example usage
if __name__ == "__main__":
    main()