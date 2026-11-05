"""Shared limits and defaults used across the Profile API."""

# Pagination for GET /v1/profiles
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# Field limits
NAME_MAX_LENGTH = 100
CITY_MAX_LENGTH = 100
EMAIL_MAX_LENGTH = 254

# Phone numbers must be in E.164 format, e.g. +14155550123
PHONE_PATTERN = r"^\+[1-9]\d{6,14}$"

# Countries are ISO 3166-1 alpha-2 codes, e.g. US, GB, DE
COUNTRY_PATTERN = r"^[A-Z]{2}$"
