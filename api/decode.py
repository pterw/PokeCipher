"""Vercel Python serverless function: ``POST {"text": "..."} -> {"result": "<plaintext>"}``."""

from api_support import make_handler
from pokecipher import decode_message

handler = make_handler(decode_message)
