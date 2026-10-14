#!/usr/bin/env python3
"""Copy completed text-only machine drafts from a local analysis directory."""
import argparse
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent


def copy_draft(source, destination):
    # Parsing first avoids importing a file while the producer is still writing it.
    draft = json.loads(source.read_text())
    if not draft.get('bvid') or not draft.get('segments') or draft.get('listening_verified') is not False:
        raise ValueError(f'Not a completed, attributed machine draft: {source.name}')
    destination.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, destination)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('analysis_directory', type=Path)
    args = parser.parse_args()
    source = args.analysis_directory
    count = 0
    for path in sorted((source / 'transcripts').glob('BV*.json')):
        improved = source / 'turbo-transcripts' / path.name
        if improved.exists():
            copy_draft(path, ROOT / 'data/alternate-transcripts' / (path.stem + '-small.json'))
            copy_draft(improved, ROOT / 'data/transcripts' / path.name)
        else:
            copy_draft(path, ROOT / 'data/transcripts' / path.name)
        count += 1
    for path in sorted((source / 'turbo-transcripts').glob('BV*.json')):
        if not (source / 'transcripts' / path.name).exists():
            copy_draft(path, ROOT / 'data/transcripts' / path.name)
            count += 1
    for path in sorted((source / 'crosschecks').glob('*.json')):
        if path.name.endswith('-raw.json'):
            continue
        copy_draft(path, ROOT / 'data/alternate-transcripts' / path.name)
    print(f'Synced {count} completed text-only source drafts; media stay outside the repository.')


if __name__ == '__main__':
    main()
