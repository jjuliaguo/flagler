"""Full Mock 4 reference solutions. Run: python solution.py"""
import re
from collections import defaultdict


# Part 1 (LC 49 Group Anagrams): build a normalized key, group by it. O(n * L log L)
def normalize_name(name):
    tokens = re.findall(r"[a-z]+", name.lower())  # drop case, punctuation, extra spaces
    return " ".join(sorted(tokens))  # sorting tokens ignores word order (like anagrams)


def normalize_dob(dob):
    # follow-up: accept "YYYY-MM-DD" and "MM/DD/YYYY"
    if "/" in dob:
        month, day, year = dob.split("/")
        return f"{year}-{int(month):02d}-{int(day):02d}"
    return dob


def group_possible_duplicates(patients):
    groups = defaultdict(list)
    for p in patients:
        key = (normalize_name(p["name"]), normalize_dob(p["dob"]))
        groups[key].append(p["id"])
    return [ids for ids in groups.values() if len(ids) > 1]


# Part 2 (LC 219 Contains Duplicate II): remember last time we saw each key. O(n)
def find_duplicate_faxes(faxes, window_min):
    last_seen = {}  # (sender, page_hash) -> received_at of most recent fax
    duplicates = []
    for fax in faxes:
        key = (fax["sender"], fax["page_hash"])
        if key in last_seen and fax["received_at"] - last_seen[key] <= window_min:
            duplicates.append(fax["id"])
        # Design choice: compare to the MOST RECENT copy (like LC 219).
        # A fax re-sent every 20 min with a 30-min window -> every resend is a duplicate.
        last_seen[key] = fax["received_at"]
    return duplicates


if __name__ == "__main__":
    patients = [
        {"id": 1, "name": "Jane Doe", "dob": "1985-03-14"},
        {"id": 2, "name": "DOE, JANE", "dob": "1985-03-14"},
        {"id": 3, "name": "John Doe", "dob": "1985-03-14"},
        {"id": 4, "name": "jane  doe", "dob": "1985-03-14"},
        {"id": 5, "name": "Jane Doe", "dob": "1990-01-01"},
    ]
    assert group_possible_duplicates(patients) == [[1, 2, 4]]
    assert group_possible_duplicates([]) == []
    assert group_possible_duplicates(patients + [{"id": 6, "name": "Jane Doe", "dob": "3/14/1985"}]) == [[1, 2, 4, 6]]
    assert normalize_name("O'Brien-Smith, Mary") == "brien mary o smith"

    faxes = [
        {"id": "A", "sender": "s1", "page_hash": "h1", "received_at": 0},
        {"id": "B", "sender": "s1", "page_hash": "h1", "received_at": 5},
        {"id": "C", "sender": "s2", "page_hash": "h1", "received_at": 10},
        {"id": "D", "sender": "s1", "page_hash": "h1", "received_at": 50},
        {"id": "E", "sender": "s1", "page_hash": "h1", "received_at": 70},
    ]
    assert find_duplicate_faxes(faxes, 30) == ["B", "E"]
    assert find_duplicate_faxes([], 30) == []
    assert find_duplicate_faxes(faxes, 0) == []
    print("mock 4: all tests passed")
