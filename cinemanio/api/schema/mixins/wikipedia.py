from django.contrib.contenttypes.models import ContentType

from cinemanio.api.schema.wikipedia import WikipediaPageNode
from cinemanio.api.utils import DjangoFilterConnectionField


class WikipediaMixin:
    wikipedia = DjangoFilterConnectionField(WikipediaPageNode)

    def resolve_wikipedia(self, info, **_):
        return WikipediaPageNode.get_queryset(info).filter(
            object_id=self.pk, content_type=ContentType.objects.get_for_model(self)
        )
