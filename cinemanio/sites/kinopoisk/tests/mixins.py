class KinopoiskSyncMixin:
    fixtures = ["kinopoisk.kinopoiskgenre.json", "kinopoisk.kinopoiskcountry.json"]

    def assert_dennis_hopper_career(self, kp_person, movie1, movie2):
        career = kp_person.person.career
        self.assertEqual(movie1.kinopoisk.id, 4220)
        self.assertEqual(movie2.kinopoisk.id, 4149)
        self.assertEqual(career.count(), 4)
        self.assertTrue(career.get(movie=movie1, role=self.director))
        self.assertTrue(career.get(movie=movie1, role=self.scenarist))
        self.assertEqual(career.get(movie=movie1, role=self.actor).name_en, "Billy")
        self.assertEqual(career.get(movie=movie2, role=self.actor).name_en, "Clifford Worley")
