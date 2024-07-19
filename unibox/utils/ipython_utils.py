from IPython.display import HTML, Image
from IPython.display import display

from PIL import Image as PILImage
from io import BytesIO

from .uni_loader import concurrent_loads

def peek_df(df, n=1):
    print(df.shape)
    print(df.columns)
    display(df.head(n))

def _src_from_data(data):
    """Base64 encodes image bytes for inclusion in an HTML img element."""
    img_obj = Image(data=data)
    for bundle in img_obj._repr_mimebundle_():
        for mimetype, b64value in bundle.items():
            if mimetype.startswith('image/'):
                return f'data:{mimetype};base64,{b64value}'

def gallery(paths: list[str], labels: list[str] = [], 
            row_height='300px', num_workers=32, debug_print=True, thumbnail_size: int = 512):
    """Shows a set of images in a gallery that flexes with the width of the notebook.
    
    Parameters
    ----------
    paths: list of str
        Paths to images to display. Can be local paths, URLs, or S3 paths.

    row_height: str
        CSS height value to assign to all images. Set to 'auto' by default to show images
        with their native dimensions. Set to a value like '250px' to make all rows
        in the gallery equal height.

    num_workers: int
        Number of concurrent workers to load images.

    debug_print: bool
        Whether to print debug information or not.
    
    thumbnail_size: int (optional)
        If provided, resize images to this size using PIL's thumbnail method.
    """
    if len(paths) > 1000:
        raise ValueError("Too many images to display.")
    
    if len(labels) > 0 and len(labels) != len(paths):
        raise ValueError("Number of labels must match number of paths.")
    
    images = concurrent_loads(paths, num_workers=num_workers, debug_print=debug_print)
    
    figures = []
    for i, image in enumerate(images):
        try:
            if thumbnail_size > 0:
                image.thumbnail((thumbnail_size, thumbnail_size))
                
            # Ensure image is in RGB mode for saving as JPEG
            if image.mode in ('RGBA', 'P'):
                image = image.convert('RGB')
                
            buffered = BytesIO()
            image.save(buffered, format="JPEG")
            img_data = buffered.getvalue()
            src = _src_from_data(img_data)
            if len(labels) > 0:
                caption_str = labels[i]
            else:
                caption_str = paths[i].split("/")[-1]
            caption = f'<figcaption style="font-size: 0.6em">{caption_str}</figcaption>'
        except Exception as e:
            src = ""
            caption = f'<figcaption style="font-size: 0.6em; color: red;">Error loading {paths[i]}: {e}</figcaption>'
        
        figures.append(f'''
            <figure style="margin: 5px !important;">
              <img src="{src}" style="height: {row_height}">
              {caption}
            </figure>
        ''')
    
    return HTML(data=f'''
        <div style="display: flex; flex-flow: row wrap; text-align: center;">
        {''.join(figures)}
        </div>
    ''')
