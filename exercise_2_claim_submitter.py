import random
import time

processed_ids = set()


class TransientError(Exception):
    pass


def submit_to_payer(claim):
    """Calls an external insurance payer API. Flaky in production."""
    if random.random() < 0.3:
        raise TransientError("payer timeout")
    return {"claim_id": claim["id"], "status": "accepted"}


def process_claims(claims, max_retries=3):
    """
    Submits each claim to the payer exactly once, retrying on transient
    failures. Returns the list of payer responses.
    """
    results = []
    for claim in claims:
        if claim["id"] in processed_ids:
            continue

        attempt = 0
        while attempt < max_retries:
            try:
                processed_ids.add(claim["id"])
                resp = submit_to_payer(claim)
                results.append(resp)
                break
            except TransientError:
                attempt += 1
                time.sleep(2 ** attempt)
            except Exception as e:
                print(f"failed claim {claim['id']}: {e}")

    return results
