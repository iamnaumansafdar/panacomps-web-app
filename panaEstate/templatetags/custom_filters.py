from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    # Check if 'dictionary' is actually a dictionary
    if isinstance(dictionary, dict):
        return dictionary.get(key, '#FFFFFF')  # Default color if key not found
    return '#FFFFFF' 

@register.filter(name='add_class')
def add_class(value, arg):
    return value.as_widget(attrs={'class': arg})