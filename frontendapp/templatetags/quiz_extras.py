from django import template
from django.utils.safestring import mark_safe
import hashlib

register = template.Library()


@register.filter
def gravatar_url(username, size=40):
    # TEMPLATE USE:  {{ email|gravatar_url:150 }}
    username_hash = hashlib.md5(username.lower().encode("utf-8")).hexdigest()
    return f"https://www.gravatar.com/avatar/{username_hash}?s={size}&d=identicon"

@register.simple_tag
def stellar_address(address):
    if address:
        html = f"""
            <button onclick="navigator.clipboard.writeText('{address}')" style="cursor:pointer;"
                class="btn btn-outline-primary btn-sm"
            >{address[:5]}...{address[-5:]}</button>
        """
    else:
        html = "<span class='badge text-bg-secondary'>No address found</span>"
    return mark_safe(html)


@register.filter
def in_category(listings, category):
    return listings.filter(listing_type=category)
