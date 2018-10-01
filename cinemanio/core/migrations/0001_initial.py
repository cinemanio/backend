# Generated by Django 2.0.1 on 2018-01-26 01:02
import caching.base
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Cast",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(blank=True, default="", max_length=300, verbose_name="Role name")),
                (
                    "name_en",
                    models.CharField(blank=True, default="", max_length=300, null=True, verbose_name="Role name"),
                ),
                (
                    "name_ru",
                    models.CharField(blank=True, default="", max_length=300, null=True, verbose_name="Role name"),
                ),
            ],
            options={
                "verbose_name": "cast",
                "verbose_name_plural": "cast",
                "ordering": ("role", "id"),
                "get_latest_by": "id",
            },
        ),
        migrations.CreateModel(
            name="Country",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="", max_length=50, verbose_name="Name")),
                ("name_en", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                ("name_ru", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                (
                    "imdb_id",
                    models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name="IMDb name"),
                ),
            ],
            options={
                "verbose_name": "country",
                "verbose_name_plural": "countries",
                "ordering": ("name",),
                "abstract": False,
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Genre",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="", max_length=50, verbose_name="Name")),
                ("name_en", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                ("name_ru", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                (
                    "imdb_id",
                    models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name="IMDb name"),
                ),
            ],
            options={"verbose_name": "genre", "verbose_name_plural": "genres", "ordering": ("name",), "abstract": False},
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Language",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="", max_length=50, verbose_name="Name")),
                ("name_en", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                ("name_ru", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                (
                    "imdb_id",
                    models.CharField(blank=True, max_length=50, null=True, unique=True, verbose_name="IMDb name"),
                ),
            ],
            options={
                "verbose_name": "language",
                "verbose_name_plural": "languages",
                "ordering": ("name",),
                "abstract": False,
            },
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Movie",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(blank=True, max_length=100, null=True, unique=True, verbose_name="Slug")),
                ("site_official_url", models.URLField(blank=True, null=True, verbose_name="Official site")),
                ("site_fan_url", models.URLField(blank=True, null=True, verbose_name="Fan site")),
                ("title", models.CharField(default="", max_length=200, verbose_name="Title")),
                ("title_en", models.CharField(default="", max_length=200, null=True, verbose_name="Title")),
                ("title_ru", models.CharField(default="", max_length=200, null=True, verbose_name="Title")),
                (
                    "year",
                    models.SmallIntegerField(
                        choices=[
                            (2028, 2028),
                            (2027, 2027),
                            (2026, 2026),
                            (2025, 2025),
                            (2024, 2024),
                            (2023, 2023),
                            (2022, 2022),
                            (2021, 2021),
                            (2020, 2020),
                            (2019, 2019),
                            (2018, 2018),
                            (2017, 2017),
                            (2016, 2016),
                            (2015, 2015),
                            (2014, 2014),
                            (2013, 2013),
                            (2012, 2012),
                            (2011, 2011),
                            (2010, 2010),
                            (2009, 2009),
                            (2008, 2008),
                            (2007, 2007),
                            (2006, 2006),
                            (2005, 2005),
                            (2004, 2004),
                            (2003, 2003),
                            (2002, 2002),
                            (2001, 2001),
                            (2000, 2000),
                            (1999, 1999),
                            (1998, 1998),
                            (1997, 1997),
                            (1996, 1996),
                            (1995, 1995),
                            (1994, 1994),
                            (1993, 1993),
                            (1992, 1992),
                            (1991, 1991),
                            (1990, 1990),
                            (1989, 1989),
                            (1988, 1988),
                            (1987, 1987),
                            (1986, 1986),
                            (1985, 1985),
                            (1984, 1984),
                            (1983, 1983),
                            (1982, 1982),
                            (1981, 1981),
                            (1980, 1980),
                            (1979, 1979),
                            (1978, 1978),
                            (1977, 1977),
                            (1976, 1976),
                            (1975, 1975),
                            (1974, 1974),
                            (1973, 1973),
                            (1972, 1972),
                            (1971, 1971),
                            (1970, 1970),
                            (1969, 1969),
                            (1968, 1968),
                            (1967, 1967),
                            (1966, 1966),
                            (1965, 1965),
                            (1964, 1964),
                            (1963, 1963),
                            (1962, 1962),
                            (1961, 1961),
                            (1960, 1960),
                            (1959, 1959),
                            (1958, 1958),
                            (1957, 1957),
                            (1956, 1956),
                            (1955, 1955),
                            (1954, 1954),
                            (1953, 1953),
                            (1952, 1952),
                            (1951, 1951),
                            (1950, 1950),
                            (1949, 1949),
                            (1948, 1948),
                            (1947, 1947),
                            (1946, 1946),
                            (1945, 1945),
                            (1944, 1944),
                            (1943, 1943),
                            (1942, 1942),
                            (1941, 1941),
                            (1940, 1940),
                            (1939, 1939),
                            (1938, 1938),
                            (1937, 1937),
                            (1936, 1936),
                            (1935, 1935),
                            (1934, 1934),
                            (1933, 1933),
                            (1932, 1932),
                            (1931, 1931),
                            (1930, 1930),
                            (1929, 1929),
                            (1928, 1928),
                            (1927, 1927),
                            (1926, 1926),
                            (1925, 1925),
                            (1924, 1924),
                            (1923, 1923),
                            (1922, 1922),
                            (1921, 1921),
                            (1920, 1920),
                            (1919, 1919),
                            (1918, 1918),
                            (1917, 1917),
                            (1916, 1916),
                            (1915, 1915),
                            (1914, 1914),
                            (1913, 1913),
                            (1912, 1912),
                            (1911, 1911),
                            (1910, 1910),
                            (1909, 1909),
                            (1908, 1908),
                            (1907, 1907),
                            (1906, 1906),
                            (1905, 1905),
                            (1904, 1904),
                            (1903, 1903),
                            (1902, 1902),
                            (1901, 1901),
                            (1900, 1900),
                            (1899, 1899),
                            (1898, 1898),
                            (1897, 1897),
                            (1896, 1896),
                            (1895, 1895),
                        ],
                        db_index=True,
                        null=True,
                        verbose_name="Year",
                    ),
                ),
                ("runtime", models.SmallIntegerField(blank=True, null=True, verbose_name="Runtime in minutes")),
                (
                    "award",
                    models.IntegerField(
                        blank=True,
                        choices=[
                            (1773, "Берлинский кинофестиваль"),
                            (8298, "Венецианский кинофестиваль"),
                            (8296, "Европейская кинопремия"),
                            (1762, "Золотой глобус"),
                            (1766, "Золотой орел"),
                            (1783, "Золотой Остап"),
                            (1768, "Каннский кинофестиваль"),
                            (1769, "Кинопремия Британской киноакадемии"),
                            (1781, "Кинопремия Международной ассоциации анимационного кино"),
                            (1763, "Кинопремия телеканала MTV"),
                            (1767, "Кинотавр"),
                            (9395, "Киношок"),
                            (1784, "Кумир"),
                            (1770, "Медный всадник"),
                            (8297, "Московский международный кинофестиваль"),
                            (1765, "Ника"),
                            (152, "Оскар"),
                            (1772, "Сатурн"),
                            (1771, "Сезар"),
                            (1764, "Эмми"),
                        ],
                        null=True,
                        verbose_name="Main award",
                    ),
                ),
                ("novel_isbn", models.IntegerField(blank=True, null=True, verbose_name="ISBN")),
                (
                    "countries",
                    models.ManyToManyField(
                        blank=True, related_name="movies", to="core.Country", verbose_name="Countries"
                    ),
                ),
                (
                    "genres",
                    models.ManyToManyField(blank=True, related_name="movies", to="core.Genre", verbose_name="Genres"),
                ),
                (
                    "languages",
                    models.ManyToManyField(
                        blank=True, related_name="movies", to="core.Language", verbose_name="Languages"
                    ),
                ),
            ],
            options={"verbose_name": "movie", "verbose_name_plural": "movies"},
        ),
        migrations.CreateModel(
            name="Person",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("slug", models.SlugField(blank=True, max_length=100, null=True, unique=True, verbose_name="Slug")),
                ("site_official_url", models.URLField(blank=True, null=True, verbose_name="Official site")),
                ("site_fan_url", models.URLField(blank=True, null=True, verbose_name="Fan site")),
                ("first_name", models.CharField(db_index=True, max_length=50, verbose_name="First name")),
                ("first_name_en", models.CharField(db_index=True, max_length=50, null=True, verbose_name="First name")),
                ("first_name_ru", models.CharField(db_index=True, max_length=50, null=True, verbose_name="First name")),
                ("last_name", models.CharField(db_index=True, max_length=50, verbose_name="Last name")),
                ("last_name_en", models.CharField(db_index=True, max_length=50, null=True, verbose_name="Last name")),
                ("last_name_ru", models.CharField(db_index=True, max_length=50, null=True, verbose_name="Last name")),
                ("biography", models.TextField(blank=True, default="", verbose_name="Biography")),
                (
                    "gender",
                    models.IntegerField(
                        blank=True, choices=[(1, "Male"), (0, "Female")], db_index=True, null=True, verbose_name="Gender"
                    ),
                ),
                ("date_birth", models.DateField(blank=True, null=True, verbose_name="Date of birth")),
                ("date_death", models.DateField(blank=True, null=True, verbose_name="Date of death")),
                (
                    "country",
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        to="core.Country",
                        verbose_name="Country of birth",
                    ),
                ),
                ("movies", models.ManyToManyField(through="core.Cast", to="core.Movie", verbose_name="Movies")),
            ],
            options={"verbose_name": "person", "verbose_name_plural": "persons", "get_latest_by": "id"},
        ),
        migrations.CreateModel(
            name="Role",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="", max_length=50, verbose_name="Name")),
                ("name_en", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                ("name_ru", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
            ],
            options={"verbose_name": "role", "verbose_name_plural": "roles", "ordering": ("name",), "abstract": False},
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.CreateModel(
            name="Type",
            fields=[
                ("id", models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("name", models.CharField(default="", max_length=50, verbose_name="Name")),
                ("name_en", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
                ("name_ru", models.CharField(default="", max_length=50, null=True, verbose_name="Name")),
            ],
            options={"verbose_name": "type", "verbose_name_plural": "types", "ordering": ("name",), "abstract": False},
            bases=(caching.base.CachingMixin, models.Model),
        ),
        migrations.AddField(
            model_name="movie",
            name="persons",
            field=models.ManyToManyField(through="core.Cast", to="core.Person", verbose_name="Persons"),
        ),
        migrations.AddField(
            model_name="movie",
            name="prequel_for",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="sequels",
                to="core.Movie",
                verbose_name="Prequel for movie",
            ),
        ),
        migrations.AddField(
            model_name="movie",
            name="remake_for",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="remakes",
                to="core.Movie",
                verbose_name="Remake of movie",
            ),
        ),
        migrations.AddField(
            model_name="movie",
            name="sequel_for",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="prequels",
                to="core.Movie",
                verbose_name="Sequel for movie",
            ),
        ),
        migrations.AddField(
            model_name="movie",
            name="types",
            field=models.ManyToManyField(blank=True, related_name="movies", to="core.Type", verbose_name="Movie types"),
        ),
        migrations.AddField(
            model_name="cast",
            name="movie",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="cast", to="core.Movie", verbose_name="Movie"
            ),
        ),
        migrations.AddField(
            model_name="cast",
            name="person",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="career",
                to="core.Person",
                verbose_name="Person",
            ),
        ),
        migrations.AddField(
            model_name="cast",
            name="role",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, related_name="roles", to="core.Role", verbose_name="Role"
            ),
        ),
        migrations.AlterUniqueTogether(name="cast", unique_together={("person", "movie", "role")}),
    ]
