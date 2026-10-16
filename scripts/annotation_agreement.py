"""Agreement on a human-created annotation CSV. Never guesses missing labels."""
import argparse
import csv
import json
from collections import Counter, defaultdict


def agreement(rows, left, right, field="topic_ai"):
    allowed = {"yes", "no", "uncertain"}
    groups = defaultdict(dict)
    skipped = 0
    for row in rows:
        if row.get("annotator_id") not in {left, right}:
            continue
        if not row.get("record_id") or row.get(field) not in allowed:
            skipped += 1
            continue
        key, person = row["record_id"], row["annotator_id"]
        if person in groups[key]:
            raise ValueError("Duplicate annotation for record and annotator: " + key)
        groups[key][person] = row[field]
    pairs = [(g[left], g[right]) for g in groups.values() if left in g and right in g]
    n = len(pairs)
    result = {"paired_records": n, "invalid_rows": skipped, "unpaired_records": len(groups)-n}
    if not n:
        return dict(result, observed_agreement=None, cohen_kappa=None, status="no_paired_annotations")
    observed = sum(a == b for a, b in pairs)/n
    a_counts, b_counts = Counter(a for a, b in pairs), Counter(b for a, b in pairs)
    expected = sum(a_counts[k]*b_counts[k] for k in allowed)/(n*n)
    return dict(result, observed_agreement=observed,
                cohen_kappa=(observed-expected)/(1-expected) if expected < 1 else None,
                status="degenerate_kappa" if expected == 1 else "computed")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("csv")
    parser.add_argument("--left", required=True)
    parser.add_argument("--right", required=True)
    args = parser.parse_args()
    if args.left == args.right:
        parser.error("Choose two distinct annotators")
    with open(args.csv, encoding="utf-8", newline="") as source:
        print(json.dumps(agreement(list(csv.DictReader(source)), args.left, args.right), indent=2))
