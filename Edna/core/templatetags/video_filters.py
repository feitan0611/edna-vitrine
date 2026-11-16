# core/templatetags/video_filters.py
from django import template
import re

register = template.Library()

@register.filter
def embed_video(url):
    if not url:
        return ''
    # YouTube
    youtube_regex = r'(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/(?:watch\?v=|embed\/)|youtu\.be\/)([^\&\?]+)'
    match = re.search(youtube_regex, url)
    if match:
        video_id = match.group(1)
        return f"https://www.youtube.com/embed/{video_id}"
    # Vimeo
    vimeo_regex = r'(?:https?:\/\/)?(?:www\.)?vimeo\.com\/(\d+)'
    match = re.search(vimeo_regex, url)
    if match:
        video_id = match.group(1)
        return f"https://player.vimeo.com/video/{video_id}"
    return url