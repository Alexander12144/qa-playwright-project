import unittest

from app.recorder.sensitive_data import is_sensitive_element, sanitize_event


class SensitiveDataTests(unittest.TestCase):
    def test_detects_password_and_sensitive_attribute_names(self):
        self.assertTrue(is_sensitive_element({"type": "password"}))
        self.assertTrue(is_sensitive_element({"name": "access_token"}))
        self.assertTrue(is_sensitive_element({"autocomplete": "cc-number"}))
        self.assertFalse(is_sensitive_element({"name": "search"}))

    def test_masks_sensitive_values_without_mutating_original_event(self):
        event = {
            "type": "input",
            "element": {"tag": "INPUT", "name": "api_key", "type": "text"},
            "value": "private-value",
        }

        safe_event = sanitize_event(event)

        self.assertEqual(safe_event["value"], "[MASKED]")
        self.assertEqual(event["value"], "private-value")

    def test_keeps_non_sensitive_values_and_masks_sensitive_change_events(self):
        ordinary = sanitize_event({"type": "input", "element": {"name": "search"}, "value": "hello"})
        sensitive = sanitize_event({"type": "change", "element": {"autocomplete": "one-time-code"}, "value": "123456"})

        self.assertEqual(ordinary["value"], "hello")
        self.assertEqual(sensitive["value"], "[MASKED]")


if __name__ == "__main__":
    unittest.main()