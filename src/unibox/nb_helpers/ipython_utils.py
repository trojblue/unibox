from io import BytesIO

from IPython.display import HTML, Image, display

from ..unibox import concurrent_loads


def peek_df(df, n=1):
    print(df.shape)
    print(df.columns)
    display(df.head(n))


def _src_from_data(data):
    """Base64 encodes image bytes for inclusion in an HTML img element."""
    img_obj = Image(data=data)
    for bundle in img_obj._repr_mimebundle_():
        for mimetype, b64value in bundle.items():
            if mimetype.startswith("image/"):
                return f"data:{mimetype};base64,{b64value}"


def _gallery(
    paths: list[str],
    labels: list[str] = [],
    row_height="300px",
    num_workers=32,
    debug_print=True,
    thumbnail_size: int = 512,
):
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
            if image is not None and image.mode in ("RGBA", "P"):
                image = image.convert("RGB")

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

        figures.append(f"""
            <figure style="margin: 5px !important;">
              <img src="{src}" style="height: {row_height}">
              {caption}
            </figure>
        """)

    display(
        HTML(
            data=f"""
        <div style="display: flex; flex-flow: row wrap; text-align: center;">
        {"".join(figures)}
        </div>
    """,
        ),
    )


import base64


def _label_gallery(
    paths: list[str],
    labels: list[str] = [],
    row_height="150px",
    num_workers=32,
    debug_print=True,
    thumbnail_size: int = 512,
):
    """Displays images in a gallery with JavaScript-based selection.

    Parameters
    ----------
    paths: list of str
        Paths to images to display. Can be local paths or URLs.
    labels: list of str
        Labels for each image. Defaults to the filename if not provided.
    row_height: str
        CSS height value to assign to all images.
    num_workers: int
        Number of concurrent workers to load images.
    debug_print: bool
        Whether to print debug information or not.
    thumbnail_size: int
        If provided, resize images to this size using PIL's thumbnail method.
    """
    if len(paths) > 1000:
        raise ValueError("Too many images to display.")

    if len(labels) > 0 and len(labels) != len(paths):
        raise ValueError("Number of labels must match number of paths.")

    # Load images using ub.concurrent_loads()
    images = concurrent_loads(paths, num_workers=num_workers)  # list of PIL images

    # convert to rgb if necessary
    for i, img in enumerate(images):
        if img is not None and img.mode in ("RGBA", "P"):
            images[i] = img.convert("RGB")

    # Process images: resize and handle None
    processed_images = []
    for img in images:
        if img is not None:
            if thumbnail_size > 0:
                img.thumbnail((thumbnail_size, thumbnail_size))
            processed_images.append(img)
        else:
            processed_images.append(None)  # Keep None for images that failed to load

    figures = []
    for i, image in enumerate(processed_images):
        if image is not None:
            try:
                buffered = BytesIO()
                image.save(buffered, format="JPEG")
                img_data = base64.b64encode(buffered.getvalue()).decode()
                src = f"data:image/jpeg;base64,{img_data}"

                if len(labels) > 0:
                    caption_str = labels[i]
                else:
                    caption_str = paths[i].split("/")[-1]

                figures.append(f"""
                    <figure style="margin: 5px !important; width: auto; text-align: center;">
                      <img src="{src}" style="height: {row_height}; cursor: pointer; box-sizing: border-box;" onclick="selectImage({i}, this)">
                      <figcaption style="font-size: 0.6em">{caption_str}</figcaption>
                    </figure>
                """)
            except Exception as e:
                figures.append(f"""
                    <figure style="margin: 5px !important;">
                      <figcaption style="font-size: 0.6em; color: red;">Error processing image {i}: {e}</figcaption>
                    </figure>
                """)
        else:
            figures.append(f"""
                <figure style="margin: 5px !important;">
                  <figcaption style="font-size: 0.6em; color: red;">Error loading image {i}</figcaption>
                </figure>
            """)

    html_content = f"""
    <div id="gallery" style="display: flex; flex-wrap: wrap; text-align: center;">
    {"".join(figures)}
    </div>
    <button onclick="copySelection()" style="margin-top: 10px;">Copy Selection</button>

    <script>
    var selectedIndices = [];

    function updateOutput() {{
        var outputDiv = document.getElementById('output');
        if (selectedIndices.length > 0) {{
            var indicesList = '[' + selectedIndices.sort((a, b) => a - b).join(', ') + ']';
            outputDiv.innerHTML = 'Selected indices: ' + indicesList;
        }} else {{
            outputDiv.innerHTML = 'Selected indices: []';
        }}
    }}

    function selectImage(index, imgElement) {{
        var idx = selectedIndices.indexOf(index);
        if (idx > -1) {{
            // Deselect
            selectedIndices.splice(idx, 1);
            imgElement.style.outline = '';
        }} else {{
            // Select
            selectedIndices.push(index);
            imgElement.style.outline = '4px solid blue';
        }}
        updateOutput();
    }}

    function copySelection() {{
        if (selectedIndices.length > 0) {{
            var indicesList = '[' + selectedIndices.sort((a, b) => a - b).join(', ') + ']';
            if (navigator.clipboard && navigator.clipboard.writeText) {{
                navigator.clipboard.writeText(indicesList).then(function() {{
                    alert('Selected indices copied to clipboard.');
                }}, function(err) {{
                    // Fallback method
                    fallbackCopyTextToClipboard(indicesList);
                }});
            }} else {{
                // Fallback method
                fallbackCopyTextToClipboard(indicesList);
            }}
        }} else {{
            alert('No images selected.');
        }}
    }}

    function fallbackCopyTextToClipboard(text) {{
        var textArea = document.createElement("textarea");
        textArea.value = text;
        textArea.style.position = "fixed";  // Avoid scrolling to bottom
        document.body.appendChild(textArea);
        textArea.focus();
        textArea.select();
        try {{
            var successful = document.execCommand('copy');
            if (successful) {{
                alert('Selected indices copied to clipboard.');
            }} else {{
                alert('Could not copy text.');
            }}
        }} catch (err) {{
            alert('Could not copy text: ', err);
        }}
        document.body.removeChild(textArea);
    }}
    </script>
    """

    display(HTML(html_content))
