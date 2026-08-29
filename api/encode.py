"""Vercel Python serverless function: ``POST {"text": "..."} -> {"result": "<ciphertext>"}``."""

from api_support import make_handler
from pokecipher import encode_message

handler = make_handler(encode_message)
