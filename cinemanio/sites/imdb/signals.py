from django.dispatch import receiver

from cinemanio.sites.imdb.tasks import search_link
from cinemanio.sites.wikipedia.models import WikipediaPage
from cinemanio.sites.wikipedia.signals import wikipedia_page_synced


@receiver(wikipedia_page_synced, sender=WikipediaPage)
def search_link_signal(content_type_id, object_id, page, **_):
    """
    Delay search IMDb links in references of wikipedia page
    """
    # https://github.com/goldsmith/Wikipedia/issues/78
    try:
        links = page.references
    except KeyError:
        return
    else:
        search_link.delay(content_type_id, object_id, links)
