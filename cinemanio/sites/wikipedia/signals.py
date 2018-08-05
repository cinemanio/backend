from django.dispatch import Signal, receiver

from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.tasks import search_roles_links

wikipedia_page_synced = Signal(providing_args=['content_type_id', 'object_id', 'lang', 'page'])


@receiver(wikipedia_page_synced, sender=WikipediaPage)
def search_link_signal(content_type_id, object_id, lang, page, **_):
    """
    Delay search Wikipedia links in references of wikipedia page
    """
    search_roles_links.delay(content_type_id, object_id, lang, page.links)
