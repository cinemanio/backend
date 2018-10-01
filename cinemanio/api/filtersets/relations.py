class RelationsMixin:
    def filter_relation(self, qs, _, value):
        return qs.filter(relations__user=self.request.user, **{f"relations__{value}": True})


def get_relations_ordering_fields(codes):
    return [[f"relations_count__{code}"] * 2 for code in codes]
