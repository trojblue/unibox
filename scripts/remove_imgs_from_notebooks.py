import json
import re

def remove_images_from_ipynb(input_path, output_path):
    """
    Remove all images from an IPython Notebook file, including images in 'data:image/' HTML blocks, 
    and save the modified content to a new file.

    Args:
        input_path (str): Path to the input .ipynb file
        output_path (str): Path to save the modified .ipynb file
    """
    # Load the notebook
    with open(input_path, 'r', encoding='utf-8') as f:
        notebook = json.load(f)

    # Regular expression to detect base64-encoded images
    image_pattern = re.compile(r'data:image/(png|jpeg|jpg|gif);base64,[a-zA-Z0-9+/=]+')

    # Iterate through cells
    for cell in notebook['cells']:
        if cell['cell_type'] == 'code':
            # Remove image outputs
            if 'outputs' in cell:
                new_outputs = []
                for output in cell['outputs']:
                    if 'data' in output:
                        # Remove image data
                        output['data'] = {k: v for k, v in output['data'].items()
                                          if not k.startswith('image/')}
                    if 'text/html' in output.get('data', {}):
                        # Remove base64-encoded images from HTML
                        output['data']['text/html'] = [
                            re.sub(image_pattern, '', line) for line in output['data']['text/html']
                        ]
                    new_outputs.append(output)
                cell['outputs'] = new_outputs
        elif cell['cell_type'] == 'markdown':
            # Remove images from markdown cells
            cell['source'] = [
                re.sub(image_pattern, '', line) for line in cell['source']
            ]

    # Save the modified notebook
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(notebook, f, indent=2)

# Example usage
# remove_images_from_ipynb("aes_raters_analysis_v3.ipynb", "aes_raters_analysis_v3_noimg.ipynb")

if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python remove_imgs_from_notebooks.py <input_path>")
    else:
        input_path = sys.argv[1]
        output_path = input_path.replace(".ipynb", "_noimg.ipynb")
        try:
            remove_images_from_ipynb(input_path, output_path)
            print(f"Images removed from {input_path} and saved to {output_path}")
        except Exception as e:
            print(f"An error occurred: {e}")