"""Tests hors-ligne du choix de « la meilleure version ». Lancer : python3 -m unittest discover -s tests"""
import importlib.machinery
import importlib.util
import unittest
from pathlib import Path
from unittest import mock

CLI = Path(__file__).resolve().parent.parent / "applemusic"
_loader = importlib.machinery.SourceFileLoader("applemusic", str(CLI))
_spec = importlib.util.spec_from_loader("applemusic", _loader)
am = importlib.util.module_from_spec(_spec)
_loader.exec_module(am)


def song(artist, title, album="Album", tid=1):
    return {"artistName": artist, "trackName": title, "collectionName": album, "trackId": tid}


def pick(query, results):
    with mock.patch.object(am, "search", return_value=results):
        r, _ = am.best(query)
    return r and r["trackId"]


class BestVersion(unittest.TestCase):
    def test_original_beats_slowed(self):
        self.assertEqual(pick("Kavinsky Nightcall", [
            song("Kavinsky", "Nightcall (Slowed)", tid=1),
            song("Kavinsky", "Nightcall", tid=2),
        ]), 2)

    def test_asked_variant_wins(self):
        self.assertEqual(pick("isq pursuit super slowed", [
            song("isq", "pursuit (slowed)", tid=1),
            song("isq", "pursuit (super slowed)", tid=2),
        ]), 2)

    def test_unrequested_parenthesis_is_a_variant(self):
        self.assertEqual(pick("Daft Punk Harder Better Faster Stronger", [
            song("Daft Punk", "Harder Better Faster Stronger (Pete Heller's Stylus)", tid=1),
            song("Daft Punk", "Harder, Better, Faster, Stronger", tid=2),
        ]), 2)

    def test_cover_by_other_artist_loses(self):
        self.assertEqual(pick("Metric Help I'm Alive", [
            song("Vitamin String Quartet", "Help, I'm Alive", tid=1),
            song("Metric", "Help I'm Alive", tid=2),
        ]), 2)

    def test_refuses_when_original_missing(self):
        self.assertIsNone(pick("Kordhell Murder In My Mind", [
            song("Firewire", "Murder (In My Mind)", tid=1),
            song("Kordhell", "FATALITY", tid=2),
        ]))

    def test_feat_is_not_a_variant(self):
        self.assertEqual(pick("Kendrick Lamar All The Stars", [
            song("Kendrick Lamar & SZA", "All The Stars (feat. SZA)", tid=1),
        ]), 1)


class ParseLine(unittest.TestCase):
    def test_formats(self):
        self.assertEqual(am.parse_line("12. Kavinsky – Nightcall"), "Kavinsky Nightcall")
        self.assertEqual(am.parse_line("Fred again.. - Marea"), "Fred again.. Marea")
        self.assertIsNone(am.parse_line("# commentaire"))
        self.assertIsNone(am.parse_line("   "))


if __name__ == "__main__":
    unittest.main()
