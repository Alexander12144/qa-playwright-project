from copy import deepcopy
import re


SENSITIVE_MARKERS = (
    "password",
    "passwd",
    "secret",
    "token",
    "authorization",
    "apikey",
    "creditcard",
    "cardnumber",
    "cvv",
    "cvc",
    "onetimecode",
    "otp",
    "securitycode",
)
SENSITIVE_AUTOCOMPLETE_VALUES = {
    "current-password",
    "new-password",
    "one-time-code",
    "cc-number",
    "cc-csc",
    "cc-exp",
}


def is_sensitive_element(element: dict | None) -> bool:
    if not isinstance(element, dict):
        return False

    input_type = str(element.get("type") or "").strip().lower()
    if input_type == "password":
        return True

    autocomplete = str(element.get("autocomplete") or "").strip().lower()
    if autocomplete in SENSITIVE_AUTOCOMPLETE_VALUES:
        return True

    values = (
        element.get("name"),
        element.get("id"),
        element.get("placeholder"),
        element.get("aria_label"),
        element.get("title"),
        element.get("autocomplete"),
        element.get("data_sensitive"),
    )
    normalized_values = [
        re.sub(r"[^a-z0-9]", "", str(value).lower())
        for value in values
        if value
    ]
    return any(
        marker in value
        for marker in SENSITIVE_MARKERS
        for value in normalized_values
    )


def sanitize_event(event: dict) -> dict:
    safe_event = deepcopy(event)
    event_type = str(safe_event.get("type") or "").lower()
    if (
        event_type in {"input", "change"}
        and safe_event.get("value") is not None
        and is_sensitive_element(safe_event.get("element"))
    ):
        safe_event["value"] = "[MASKED]"
    return safe_event