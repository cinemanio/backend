import datetime

from cinemanio.core.factories import MovieFactory, CastFactory
from cinemanio.core.models import Movie, Cast, Role
from cinemanio.core.tests.base import BaseTestCase
from cinemanio.sites.imdb.factories import ImdbMovieFactory, ImdbPersonFactory

USA_ID = 98
MATRIX_ID = 133093


class ImdbImporterTest(BaseTestCase):
    def test_get_movie_matrix(self):
        """
        Get basic movie data from IMDB - Matrix
        """
        imdb_movie = ImdbMovieFactory(id=MATRIX_ID, movie__year=None)
        imdb_movie.import_data()

        self.assertEqual(imdb_movie.movie.title, 'The Matrix')
        # self.assertEqual(imdb_movie.movie.title_ru, u'Матрица')
        self.assertEqual(imdb_movie.movie.year, 1999)
        self.assertEqual(imdb_movie.movie.runtime, 136)
        self.assertEqual(imdb_movie.movie.imdb.rating, 8.7)
        self.assertQuerysetEqual(imdb_movie.movie.genres.all(), ['Action', 'Sci-Fi'])
        self.assertQuerysetEqual(imdb_movie.movie.languages.all(), ['English'])
        self.assertQuerysetEqual(imdb_movie.movie.countries.all(), ['USA'])
        self.assertQuerysetEqual(imdb_movie.movie.types.all(), [])
        # self.assertEqual(imdb_movie.movie.russia_start, datetime.date(1999, 10, 14))

    def test_get_movie_runtime(self):
        """
        Get basic movie data from IMDB - runtime in format "xxxxx:17"
        """
        imdb_movie = ImdbMovieFactory(id=1524546)
        imdb_movie.import_data()
        self.assertEqual(imdb_movie.movie.runtime, 17)

    # TODO: strange test
    # def test_get_movie_black_white_types1(self):
    #     imdb_object = ImdbMovie(Movie(), 64276)
    #     initial = imdb_object.get_applied_data()
    #     self.assertEqual(initial.get('types'), [])

    # TODO: strange test
    # def test_get_movie_black_white_types2(self):
    #     imdb_object = ImdbMovie(Movie(), 2076220)
    #     initial = imdb_object.get_applied_data()
    #     self.assertEqual(initial.get('types'), [])

    def test_get_person(self):
        """
        Get basic movie data from IMDB - Dennis Hopper
        """
        imdb_person = ImdbPersonFactory(id=454)
        imdb_person.import_data()

        self.assertEqual(imdb_person.person.first_name_en, 'Dennis')
        self.assertEqual(imdb_person.person.last_name_en, 'Hopper')
        self.assertEqual(imdb_person.person.date_birth, datetime.date(1936, 5, 17))
        self.assertEqual(imdb_person.person.date_death, datetime.date(2010, 5, 29))
        self.assertEqual(imdb_person.person.country.id, USA_ID)

    # def test_admin_command_and_multirelation_objects(self):
    #     """
    #     Тест на назначение и сохранение связанных объектов и на дополнение информации с imdb через админ-комманду
    #     1. Дополняем пустой объект данными с IMDb и сохраняем
    #     2. Заново получаем дополненный объект и проверяем его мульти-отношения и дату старта проката
    #     3. Очищаем мульти-отношения и дату, запускаем админ-комманду на дополнение
    #     4. Получаем объект из локальной базы и проверяем дату и мульти-отношения
    #     """
    #     object = Movie()
    #     ImdbMovie(object, self.movie['id']).get_applied_data()
    #     object.save()
    #
    #     imdb_object = ImdbMovie(object, self.movie['id'])
    #     initial = imdb_object.get_applied_data()
    #     self.assertEqual(initial.get('languages'), self.movie['languages'])
    #     self.assertEqual(object.languages.count(), 1)
    #     self.assertEqual(list(object.languages.all().values_list('id', flat=True)), self.movie['languages'])
    #
    #     self.assertEqual(initial.get('russia_start'), datetime.date(1999, 10, 14))
    #     self.assertEqual(object.russia_start, datetime.date(1999, 10, 14))
    #
    #     # clear all multirelation-object
    #     object.languages.clear()
    #     object.russia_start = None
    #     self.assertEqual(object.languages.count(), 0)
    #     command = Command()
    #     command.import_data(object)
    #     self.assertEqual(object.languages.count(), 1)
    #     self.assertEqual(object.russia_start, datetime.date(1999, 10, 14))
    #
    #     # get object from local database
    #     object = Movie.objects.get(imdb_id=self.movie['id'])
    #     self.assertEqual(object.russia_start, datetime.date(1999, 10, 14))
    #     self.assertEqual(list(object.languages.all().values_list('id', flat=True)), self.movie['languages'])

    # TODO: no cast, only directors waiting for https://github.com/alberanid/imdbpy/issues/103
    # def test_add_roles_to_movie_by_imdb(self):
    #     movie = MovieFactory()
    #
    #     # director, producer, writer
    #     imdb_person1 = ImdbPersonFactory(id=905152)
    #     # Neo
    #     imdb_person2 = ImdbPersonFactory(id=206)
    #
    #     ImdbMovie(movie, MATRIX_ID).get_applied_data(roles=True)
    #
    #     self.assertEqual(Cast.objects.count(), 4)
    #     self.assertTrue(movie.cast.get(person=imdb_person1.person, role=Role.objects.get_director()))
    #     self.assertEqual(movie.cast.get(person=imdb_person2.person, role=Role.objects.get_actor()).role_en, 'Neo')

    # TODO: no cast, only directors waiting for https://github.com/alberanid/imdbpy/issues/103
    # def test_add_roles_to_movie_by_names(self):
    #     # Neo
    #     person1 = PersonFactory(first_name_en=u'Keanu', last_name_en=u'Reeves')
    #     person2 = PersonFactory(first_name_en=u'Jeremy', last_name_en=u'Ball')
    #     movie = MovieFactory()
    #
    #     role = Role.objects.get_actor()
    #
    #     ImdbMovie(movie, MATRIX_ID).get_applied_data(roles=True)
    #
    #     self.assertEqual(Cast.objects.count(), 2)
    #
    #     role1 = Cast.objects.get(person=person1, movie=movie, role=role)
    #
    #     person1 = Person.objects.get(id=person1.id)
    #     self.assertEqual(person1.imdb.id, 206)
    #     self.assertEqual(role1.role_en, 'Neo')
    #
    #     role2 = Cast.objects.get(person=person2, movie=movie, role=role)
    #
    #     person2 = Person.objects.get(id=person2.id)
    #     self.assertEqual(person2.imdb.id, 50390)
    #     self.assertEqual(role2.role_en, 'Businessman')

    def test_add_roles_to_person_by_imdb(self):
        # Easy rider: director, Billy, writer
        imdb_movie1 = ImdbMovieFactory(id=64276)
        # True Romance: Clifford Worley
        imdb_movie2 = ImdbMovieFactory(id=108399)

        imdb_person = ImdbPersonFactory(id=454)
        imdb_person.import_data(roles=True)

        career = imdb_person.person.career
        self.assertEqual(career.count(), 4)
        self.assertTrue(career.get(movie=imdb_movie1.movie, role=Role.objects.get_director()))
        self.assertTrue(career.get(movie=imdb_movie1.movie, role=Role.objects.get_author()))
        self.assertEqual(career.get(movie=imdb_movie1.movie, role=Role.objects.get_actor()).name_en, 'Billy')
        self.assertEqual(career.get(movie=imdb_movie2.movie, role=Role.objects.get_actor()).name_en, 'Clifford Worley')

    # TODO: authors ar not recognized properly, only as scenarists, cause imdb_person.notes are empty
    # def test_add_writers_to_movie(self):
    #     movie = MovieFactory()
    #     # writer, Dostoevskiy
    #     imdb_person1 = ImdbPersonFactory(id=234502)
    #
    #     ImdbMovie(movie, '0475730').get_applied_data(roles=True)
    #     self.assertTrue(movie.cast.get(person=imdb_person1.person, role=Role.objects.get_author()))

    def test_add_movies_to_writer(self):
        # writer, Dostoevskiy
        imdb_movie = ImdbMovieFactory(id=475730)
        imdb_person = ImdbPersonFactory(id=234502)
        imdb_person.import_data(roles=True)

        self.assertTrue(imdb_person.person.career.filter(movie=imdb_movie.movie, role=Role.objects.get_author()))

    def test_add_roles_to_person_of_movie_by_name(self):
        movie1 = MovieFactory(title_en=u'Easy Rider')
        movie2 = MovieFactory(title_en=u'True Romance')
        imdb_person = ImdbPersonFactory(id=454)

        role = Role.objects.get_actor()
        CastFactory(person=imdb_person.person, movie=movie1, role=role)

        self.assertEqual(Cast.objects.count(), 1)

        imdb_person.import_data(roles=True)

        self.assertEqual(Cast.objects.count(), 4)

        movie1 = Movie.objects.get(id=movie1.id)
        self.assertEqual(movie1.imdb.id, 64276)

        movie2 = Movie.objects.get(id=movie2.id)
        self.assertEqual(movie2.imdb.id, 108399)

        self.assertEqual(imdb_person.person.career.get(movie=movie1, role=role).name_en, 'Billy')
        self.assertEqual(imdb_person.person.career.get(movie=movie2, role=role).name_en, 'Clifford Worley')

    # TODO: imdb stop returns original title for this movie
    # def test_movie_title_en(self):
    #     imdb_movie = ImdbMovieFactory(id=190332)
    #     imdb_movie.import_data()
    #
    #     self.assertEqual(imdb_movie.movie.title, 'Wo hu cang long')
    #     self.assertEqual(imdb_movie.movie.title_en, 'Crouching Tiger, Hidden Dragon')
