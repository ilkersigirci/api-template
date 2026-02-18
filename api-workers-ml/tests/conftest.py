import os

from api_shared.utils.test_tokens import generate_hatchet_test_token

os.environ.setdefault("HATCHET_CLIENT_TOKEN", generate_hatchet_test_token())
