#!/usr/bin/env python3
"""
Build Kosh's offline dictionary from WordNet.

Output: dict/a.json ... dict/z.json, dict/_.json, dict/index.json

Shape of each shard, matching what index.html already renders:
  { "abandon": [ {"partOfSpeech":"verb",
                  "definitions":[{"definition":"...","example":"..."}],
                  "synonyms":["forsake","desert"]} ] }

WordNet is chosen over Webster's 1913 (the other common free option) because
1913 English is full of archaic and obsolete senses — useless for studying
modern vocabulary. WordNet is modern, concise, and includes example sentences.
"""

import json
import os
import re
from collections import defaultdict

import nltk

nltk.download("wordnet", quiet=True)
nltk.download("omw-1.4", quiet=True)

from nltk.corpus import wordnet as wn

POS_NAMES = {
    "n": "noun",
    "v": "verb",
    "a": "adjective",
    "s": "adjective",
    "r": "adverb",
}

MAX_DEFS_PER_POS = 4      # keeps file size down; the common senses come first
MAX_SYNONYMS = 6
OUT_DIR = "dict"

# word -> partOfSpeech -> {"definitions": [...], "synonyms": set()}
entries = defaultdict(lambda: defaultdict(lambda: {"definitions": [], "synonyms": []}))


def clean(text):
    text = re.sub(r"\s+", " ", text or "").strip()
    return text


print("Reading WordNet synsets...")
synset_count = 0
for synset in wn.all_synsets():
    synset_count += 1
    pos = POS_NAMES.get(synset.pos())
    if not pos:
        continue

    definition = clean(synset.definition())
    if not definition:
        continue

    examples = [clean(e) for e in synset.examples()]
    example = examples[0] if examples else ""

    lemma_names = [l.name().replace("_", " ") for l in synset.lemmas()]

    for name in lemma_names:
        # Skip multi-word phrases beyond 3 words, and anything with odd chars.
        if len(name.split()) > 3:
            continue
        key = name.lower()
        if not key or not re.match(r"^[a-z0-9' \-\.]+$", key):
            continue

        bucket = entries[key][pos]
        if len(bucket["definitions"]) < MAX_DEFS_PER_POS:
            bucket["definitions"].append({"definition": definition, "example": example})
        for syn in lemma_names:
            s = syn.lower()
            if s != key and syn not in bucket["synonyms"] and len(bucket["synonyms"]) < MAX_SYNONYMS:
                bucket["synonyms"].append(syn)

print(f"  {synset_count:,} synsets -> {len(entries):,} headwords")

# ---- reshape into the app's format and shard by first letter ----
shards = defaultdict(dict)

for word, by_pos in entries.items():
    meanings = []
    # noun/verb/adjective/adverb in a stable, familiar order
    for pos in ("noun", "verb", "adjective", "adverb"):
        if pos in by_pos:
            meanings.append({
                "partOfSpeech": pos,
                "definitions": by_pos[pos]["definitions"],
                "synonyms": by_pos[pos]["synonyms"],
            })
    if not meanings:
        continue

    first = word[0]
    letter = first if "a" <= first <= "z" else "_"
    shards[letter][word] = meanings

os.makedirs(OUT_DIR, exist_ok=True)

# Clear out any stale shards from a previous build
for existing in os.listdir(OUT_DIR):
    if existing.endswith(".json"):
        os.remove(os.path.join(OUT_DIR, existing))

total_bytes = 0
written = []
for letter in sorted(shards):
    path = os.path.join(OUT_DIR, f"{letter}.json")
    # separators=(",",":") strips all whitespace — meaningfully smaller download
    with open(path, "w", encoding="utf-8") as f:
        json.dump(shards[letter], f, ensure_ascii=False, separators=(",", ":"))
    size = os.path.getsize(path)
    total_bytes += size
    written.append(letter)
    print(f"  dict/{letter}.json  {len(shards[letter]):>7,} words  {size/1024/1024:>6.2f} MB")

index = {
    "shards": written,
    "words": sum(len(s) for s in shards.values()),
    "approx_mb": round(total_bytes / 1024 / 1024, 1),
    "source": "WordNet 3.0, Princeton University",
}
with open(os.path.join(OUT_DIR, "index.json"), "w", encoding="utf-8") as f:
    json.dump(index, f, ensure_ascii=False)

print(f"\nDone: {index['words']:,} words, {index['approx_mb']} MB total across {len(written)} shards.")
if total_bytes / 1024 / 1024 > 90:
    print("WARNING: shards are large; consider lowering MAX_DEFS_PER_POS.")
