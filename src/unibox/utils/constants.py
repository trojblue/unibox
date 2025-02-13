"""commonly used constant variables"""

__all_imgs_raw = "jpg jpeg png bmp dds exif jp2 jpx pcx pnm ras gif tga tif tiff xbm xpm webp jpe"
IMG_FILES = ["." + i.strip() for i in __all_imgs_raw.split(" ")]

# new name
IMAGE_FILES = IMG_FILES

__all_videos_raw = "webm mkv flv vob ogv ogg avi mov qt wmv yuv rm rmvb asf m4v mpeg mp4 mpe mpg m2v 3gp 3g2"
VIDEO_FILES = ["." + i.strip() for i in __all_videos_raw.split(" ")]

__all_audio_raw = "mp3 wav aac flac ogg wma m4a aiff au opus alac amr ac3"
AUDIO_FILES = ["." + i.strip() for i in __all_audio_raw.split(" ")]