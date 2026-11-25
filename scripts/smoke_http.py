"""Check the cipher HTTP contract through a running web deployment."""

import argparse
import json
from urllib.request import Request, urlopen

# Fixed published-encoder output for "hello world this is a test of the cipher".
OVER_BUDGET_CIPHERTEXT = (
    "Tentacruel Weepinbell Ponyta Gyarados Slowbro Bulbasaur Grimer Slowpoke Farfetch'd "
    "Medicham Bellsprout Chikorita Dodrio Poliwhirl Geodude Doduo Treecko Poliwrath Gloom "
    "Bulbasaur Machop Chikorita Vileplume Paras Voltorb Electrode Treecko Plusle Victreebel "
    "Bulbasaur Dodrio Machop Aron Chikorita Machamp Machoke Magnemite Tentacruel Weepinbell Oddish"
)
OVER_BUDGET_RESULT = "hello wnrld this ]s [a,h] test {o}[a,f] t[a,h]e cbphe[J,r]"


def request_json(url: str, text: str | None = None) -> dict[str, object]:
    """Fetch a JSON object and require HTTP 200 from the requested endpoint."""
    request = Request(url)
    if text is not None:
        request = Request(
            url,
            data=json.dumps({"text": text}).encode(),
            headers={"Content-Type": "application/json"},
        )
    with urlopen(request, timeout=10) as response:
        if response.status != 200:
            raise AssertionError(f"{url} returned HTTP {response.status}")
        payload = json.load(response)
    if not isinstance(payload, dict):
        raise AssertionError(f"{url} returned a non-object response")
    return payload


def check_smart_punctuation(api_url: str) -> None:
    """Given the public vocabulary, when smart punctuation is pasted, then it decodes cleanly."""
    vocabulary = request_json(f"{api_url}/names")
    names, folds = vocabulary.get("names"), vocabulary.get("folds")
    if not isinstance(names, list) or "Farfetch'd" not in names:
        raise AssertionError("The vocabulary must include the canonical Farfetch'd spelling")
    if not isinstance(folds, dict) or folds.get("’") != "'":
        raise AssertionError("The vocabulary must advertise the smart-apostrophe mapping")

    result = request_json(f"{api_url}/decode", "Farfetch’d Zubat")
    if result != {"result": "rH"}:
        raise AssertionError(f"Expected an unflagged smart-punctuation decode, got {result!r}")


def check_branch_budget(api_url: str) -> None:
    """Given over-budget ciphertext, when decoded, then the result carries the budget flag."""
    result = request_json(f"{api_url}/decode", OVER_BUDGET_CIPHERTEXT)
    if result.get("result") != OVER_BUDGET_RESULT or result.get("truncated") is not True:
        raise AssertionError(
            f"Expected the best-effort result with truncated: true, got {result!r}"
        )


def main() -> None:
    """Run both smoke cases against the web origin supplied on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("base_url", help="Web origin, such as http://127.0.0.1:3000")
    args = parser.parse_args()
    api_url = f"{args.base_url.rstrip('/')}/api"
    check_smart_punctuation(api_url)
    check_branch_budget(api_url)
    print("HTTP smoke passed for smart punctuation and branch-budget reporting")


if __name__ == "__main__":
    main()
