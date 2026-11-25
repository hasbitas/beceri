import itertools
import unittest

import solution


class TurkishCaseTests(unittest.TestCase):
    def test_four_i_characters(self):
        for text, upper, lower in [
            ("i", "İ", "i"), ("İ", "İ", "i"),
            ("ı", "I", "ı"), ("I", "I", "ı"),
            ("iİıI", "İİII", "iiıı"),
            ("istanbul IĞDIR İzmir", "İSTANBUL IĞDIR İZMİR", "istanbul ığdır izmir"),
        ]:
            with self.subTest(text=text):
                self.assertEqual(solution.tr_upper(text), upper)
                self.assertEqual(solution.tr_lower(text), lower)

    def test_empty_and_nonletters(self):
        for text in ["", " \t\n\r", "0123 !?", "\x00🙂中\ud800\udfff"]:
            with self.subTest(text=repr(text)):
                self.assertEqual(solution.tr_upper(text), text)
                self.assertEqual(solution.tr_lower(text), text)






    def test_subclasses_and_call_independence(self):
        class Text(str):
            pass

        original = Text("Iİiı ΟΣ")
        for _ in range(3):
            self.assertEqual(solution.tr_upper(original), "IİİI ΟΣ")
            self.assertEqual(solution.tr_lower(original), "ıiiı ος")
            self.assertEqual(original, "Iİiı ΟΣ")
            self.assertIsInstance(solution.tr_upper(original), str)
            self.assertIsInstance(solution.tr_lower(original), str)


if __name__ == "__main__":
    unittest.main()
