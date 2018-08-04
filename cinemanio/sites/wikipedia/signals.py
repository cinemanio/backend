from django.dispatch import Signal

wikipedia_page_synced = Signal(providing_args=['content_type_id', 'object_id', 'page'])
