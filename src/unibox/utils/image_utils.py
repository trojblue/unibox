from PIL import Image, ImageDraw, ImageFont


def concatenate_images_horizontally(images, max_height=1024) -> Image.Image:
    """Concatenates a list of PIL.Image objects horizontally, ensuring no image exceeds a specified maximum height.

    :param images: List of PIL.Image objects.
    :param max_height: Maximum height for any image in the list. Images taller than this will be resized proportionally.
    :return: A single PIL.Image object resulting from the horizontal concatenation.
    """
    if not images:
        print("No images to concatenate.")
        return None

    resized_images = []

    # Resize images if necessary to ensure no image exceeds the max height
    for image in images:
        if image.height > max_height:
            aspect_ratio = image.width / image.height
            new_width = int(aspect_ratio * max_height)
            resized_image = image.resize((new_width, max_height))
            resized_images.append(resized_image)
        else:
            resized_images.append(image)

    # Determine the total width and the maximum height of resized images
    total_width = sum(image.width for image in resized_images)
    max_height = max(image.height for image in resized_images)

    # Create a new image with the appropriate dimensions
    concatenated_image = Image.new("RGB", (total_width, max_height))

    # Paste each resized image into the new image
    x_offset = 0
    for image in resized_images:
        concatenated_image.paste(image, (x_offset, 0))
        x_offset += image.width

    return concatenated_image


def textsize(text, font):
    im = Image.new(mode="P", size=(0, 0))
    draw = ImageDraw.Draw(im)
    _, _, width, height = draw.textbbox((0, 0), text=text, font=font)
    return width, height


def get_font_size(text, max_width, max_height, base_font, size_adjustment):
    if len(text) < 7:
        text = text + "a" * (7 - len(text))  # if text to short, add spaces to make it longer (to void oversized font)

    font_size = 1
    while True:
        temp_font = base_font.font_variant(size=font_size)
        text_width, text_height = textsize(text, temp_font)
        if text_width > max_width or text_height > max_height:
            break
        font_size += 1

    if size_adjustment == "default":
        font_size = font_size
    elif size_adjustment == "larger":
        font_size = min(font_size + 10, font_size * 2)  # Increase the font size
    elif size_adjustment == "smaller":
        font_size = max(font_size - 10, font_size // 2)  # Decrease the font size
    elif size_adjustment == "smallest":
        font_size = max(font_size - 30, 1)  # Decrease the font size
    elif size_adjustment == "largest":
        font_size = min(font_size + 30, font_size * 3)  # Increase the font size

    return base_font.font_variant(size=font_size - 1)


def calculate_text_position(img_width, img_height, text_width, text_height, position, alignment, padding):
    if position in ["top", "bottom"]:
        text_y = padding / 2 if position == "top" else img_height + padding / 2
        if alignment == "left":
            text_x = padding / 2
        elif alignment == "right":
            text_x = img_width - text_width - padding / 2
        else:  # 'center'
            text_x = (img_width - text_width) / 2
    else:
        text_y = (img_height - text_height) / 2
        text_x = padding / 2 if position == "left" else img_width + padding / 2

    return text_x, text_y


def create_new_image_with_space(pil_image, max_width, max_height, padding, position, text_height):
    img_width, img_height = pil_image.size
    if position in ["top", "bottom"]:
        new_image = Image.new("RGB", (img_width, img_height + text_height + padding), (255, 255, 255))
        new_image.paste(pil_image, (0, text_height + padding) if position == "top" else (0, 0))
    else:
        new_image = Image.new("RGB", (img_width + max_width + padding, img_height), (255, 255, 255))
        new_image.paste(pil_image, (max_width + padding, 0) if position == "left" else (0, 0))
    return new_image


def load_font():
    try:
        font_path = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"  # Common path on many Linux systems
        return ImageFont.truetype(font_path, 1)  # Start with a small size to calculate the proper size
    except OSError:
        return ImageFont.load_default()


def add_annotation(
    pil_image: Image.Image, annotation: str, position: str = "top", alignment: str = "center", size: str = "default"
):
    """Adds a single annotation string as text to the top, left, right, or bottom of the image.
    Adjusts font size automatically according to actual image size to make it easy to look.

    Parameters:
    pil_image (Image.Image): The image to annotate.
    annotation (str): The annotation text.
    position (str): The position where the annotation should be added ('top', 'left', 'right', 'bottom').
    alignment (str): The alignment of the text ('center', 'left', 'right'). 'left' and 'right' are only valid for top and bottom positions.
    text_size (str): The size of the text ('larger', 'default', 'smaller', 'smallest', 'largest').
    """
    font = load_font()
    img_width, img_height = pil_image.size

    # Calculate the maximum width and height for the text
    max_width = img_width if position in ["top", "bottom"] else img_width // 5
    max_height = img_height // 10 if position in ["top", "bottom"] else img_height

    font = get_font_size(annotation, max_width, max_height, font, size)
    text_width, text_height = textsize(annotation, font)

    padding = 10  # Add padding around the text
    text_x, text_y = calculate_text_position(
        img_width, img_height, text_width, text_height, position, alignment, padding
    )

    new_image = create_new_image_with_space(pil_image, max_width, max_height, padding, position, text_height)
    draw = ImageDraw.Draw(new_image)
    draw.text((text_x, text_y), annotation, fill="black", font=font)

    return new_image


def add_annotations(pil_image: Image.Image, annotations: list, position: str = "top"):
    """Adds multiple annotation strings as text to the top, left, right, or bottom of the image.
    Adjusts font size automatically according to actual image size to make it easy to look.

    Parameters:
    pil_image (Image.Image): The image to annotate.
    annotations (list): List of tuples containing the annotation text, alignment, and text size.
    position (str): The position where the annotation should be added ('top', 'left', 'right', 'bottom').
    """
    font = load_font()
    img_width, img_height = pil_image.size

    # Calculate the maximum width and height for the text
    max_width = img_width if position in ["top", "bottom"] else img_width // 5
    max_height = img_height // 10 if position in ["top", "bottom"] else img_height

    padding = 10  # Add padding around the text

    # Calculate the maximum height of all annotations to align them properly
    max_text_height = 0
    for annotation, _, size in annotations:
        font = get_font_size(annotation, max_width, max_height, font, size)
        _, text_height = textsize(annotation, font)
        max_text_height = max(max_text_height, text_height)

    new_image = create_new_image_with_space(pil_image, max_width, max_height, padding, position, max_text_height)
    draw = ImageDraw.Draw(new_image)

    for annotation, align, size in annotations:
        font = get_font_size(annotation, max_width, max_height, font, size)
        text_width, text_height = textsize(annotation, font)
        text_x, text_y = calculate_text_position(
            img_width, img_height, text_width, max_text_height, position, align, padding
        )
        draw.text((text_x, text_y), annotation, fill="black", font=font)

    return new_image
