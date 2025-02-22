import markdown
from django import template
from django.utils.safestring import mark_safe
import re
from bs4 import BeautifulSoup
from ..utils import clean_slug

register = template.Library()

@register.filter(name='markdown')
def markdown_format(text):
    return mark_safe(markdown.markdown(text, extensions=['extra']))

@register.filter
def get_headings(content):
    soup = BeautifulSoup(content, 'html.parser')
    headings = []
    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        level = int(tag.name[1])
        text = tag.get_text()
        slug = clean_slug(text)
        headings.append({
            'level': level,
            'text': text,
            'slug': slug
        })
    return headings

@register.filter
def add_heading_anchors(content):
    soup = BeautifulSoup(content, 'html.parser')
    for tag in soup.find_all(['h2', 'h3', 'h4', 'h5', 'h6']):
        text = tag.get_text()
        slug = clean_slug(text)
        
        # Create anchor
        anchor = soup.new_tag('a', href=f'#{slug}')
        anchor['class'] = 'heading-anchor'
        anchor['aria-hidden'] = 'true'
        anchor.string = '#'
        
        # Add id to heading and append anchor
        tag['id'] = slug
        tag.append(anchor)
    
    return str(soup)

@register.filter(name='multiply')
def multiply(value, arg):
    return int(value) * int(arg)
