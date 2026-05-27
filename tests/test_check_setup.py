import unittest

from tools.check_setup import _validate_mapping_entry


class MappingValidationTest(unittest.TestCase):
    def test_coordinate_mapping_accepts_known_profile_key(self) -> None:
        errors = _validate_mapping_entry(
            {
                "field_key": "full_name",
                "method": "coordinate",
                "page": 0,
                "x": 150,
                "y": 200,
                "font_size": 12,
            },
            0,
            {"full_name": "山田 太郎"},
            "sample",
        )

        self.assertEqual(errors, [])

    def test_missing_profile_key_is_reported(self) -> None:
        errors = _validate_mapping_entry(
            {"field_key": "unknown", "method": "form_field", "field_name": "name"},
            1,
            {"full_name": "山田 太郎"},
            "sample",
        )

        self.assertIn("sample: profile key not found for mappings[1]: unknown", errors)

    def test_coordinate_mapping_requires_numeric_position(self) -> None:
        errors = _validate_mapping_entry(
            {"field_key": "full_name", "method": "coordinate", "page": 0, "x": "left", "y": 200},
            2,
            {"full_name": "山田 太郎"},
            "sample",
        )

        self.assertIn("sample: mappings[2].x must be numeric", errors)


if __name__ == "__main__":
    unittest.main()
