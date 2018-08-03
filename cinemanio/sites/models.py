from django.db import models


class SitesBaseManager(models.Manager):
    def safe_create(self, id, movie):
        try:
            movie_exist = self.get(id=id)
            raise PossibleDuplicate(
                f"Can not assign IMDb ID={id} to movie ID={movie.id}, "
                f"because it's already assigned to movie ID={movie_exist.movie.id}")
        except self.model.DoesNotExist:
            return self.create(id=id, movie=movie)
