from graphene import String
from graphene_django import DjangoObjectType

from cinemanio.api.utils import DjangoObjectTypeMixin
from cinemanio.sites.wikipedia.models import WikipediaPage


class WikipediaPageNode(DjangoObjectTypeMixin, DjangoObjectType):
    url = String()

    class Meta:
        model = WikipediaPage
        filter_fields = ('lang',)
        only_fields = ('lang', 'title', 'content')
        use_connection = True
