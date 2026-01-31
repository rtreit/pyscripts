import argparse
import time
from datetime import datetime, timezone
from pathlib import Path

import requests

API = "https://api.chess.com/pub/player/{username}/games/archives"


def get_json(session: requests.Session, url: str) -> dict:
    for attempt in range(1, 8):
        r = session.get(url, timeout=30)
        if r.status_code == 200:
            return r.json()

        # chess.com can return 429 if you hammer it
        if r.status_code in (429, 500, 502, 503, 504):
            wait = min(2 ** attempt, 30)
            print(f"  {r.status_code} on {url} -> sleeping {wait}s (attempt {attempt})")
            time.sleep(wait)
            continue

        r.raise_for_status()

    raise RuntimeError(f"Failed too many times: {url}")


def extract_game_url(pgn: str) -> str | None:
    """Extract the game URL from a PGN string."""
    for line in pgn.split("\n"):
        if line.startswith("[Link "):
            # Extract URL from [Link "https://..."]
            start = line.find('"') + 1
            end = line.rfind('"')
            if start > 0 and end > start:
                return line[start:end]
    return None


def extract_game_timestamp(pgn: str) -> int | None:
    """Extract a Unix timestamp from a PGN's EndDate and EndTime headers."""
    end_date = None
    end_time = None
    
    for line in pgn.split("\n"):
        if line.startswith("[EndDate "):
            # Extract date from [EndDate "2026.01.31"]
            start = line.find('"') + 1
            end = line.rfind('"')
            if start > 0 and end > start:
                end_date = line[start:end]
        elif line.startswith("[EndTime "):
            # Extract time from [EndTime "01:32:29"]
            start = line.find('"') + 1
            end = line.rfind('"')
            if start > 0 and end > start:
                end_time = line[start:end]
    
    if end_date and end_time:
        try:
            # Combine date and time: "2026.01.31 01:32:29"
            dt_str = f"{end_date} {end_time}"
            dt = datetime.strptime(dt_str, "%Y.%m.%d %H:%M:%S")
            return int(dt.timestamp())
        except ValueError:
            pass
    
    return None


def find_most_recent_timestamp(out_path: Path) -> int | None:
    """Find the timestamp of the most recent game in the existing PGN file."""
    if not out_path.exists():
        return None

    most_recent = None
    try:
        # Read from the end to find recent games more quickly
        with out_path.open("r", encoding="utf-8") as f:
            # Seek to near the end of file (last 50KB should contain several games)
            f.seek(0, 2)  # Go to end
            file_size = f.tell()
            chunk_size = min(100000, file_size)  # Read last 100KB max
            f.seek(max(0, file_size - chunk_size))
            
            # Read the chunk and split into games
            chunk = f.read()
            
            # Split by double newlines to get PGN blocks
            # We might start mid-game, so skip first incomplete one
            games = chunk.split("\n\n")
            
            # Process from end (most recent) backwards
            for pgn_text in reversed(games):
                if "[Event " in pgn_text:  # Make sure it's a valid PGN block
                    timestamp = extract_game_timestamp(pgn_text)
                    if timestamp and (most_recent is None or timestamp > most_recent):
                        most_recent = timestamp
                        # We found at least one, but keep checking in case they're out of order
            
    except Exception as e:
        print(f"Warning: Could not read existing file for timestamp: {e}")
        return None

    if most_recent:
        dt = datetime.fromtimestamp(most_recent, timezone.utc)
        print(f"Most recent game: {dt.strftime('%Y-%m-%d %H:%M:%S')} (timestamp: {most_recent})")
    else:
        print("Warning: Could not find any game timestamps in existing file")
    
    return most_recent


def parse_archive_year_month(url: str) -> tuple[int, int] | None:
    """Extract (year, month) from an archive URL like .../games/2026/01."""
    parts = url.rstrip("/").split("/")
    if len(parts) < 2:
        return None
    try:
        year = int(parts[-2])
        month = int(parts[-1])
        if 1 <= month <= 12:
            return year, month
    except ValueError:
        return None
    return None


def filter_archives_by_cutoff(archives: list[str], cutoff_timestamp: int | None) -> list[str]:
    """Return only archives for months at/after the cutoff month (UTC)."""
    if not cutoff_timestamp:
        return archives

    cutoff_dt = datetime.fromtimestamp(cutoff_timestamp, timezone.utc)
    cutoff_year = cutoff_dt.year
    cutoff_month = cutoff_dt.month

    filtered: list[str] = []
    for url in archives:
        ym = parse_archive_year_month(url)
        if not ym:
            filtered.append(url)
            continue
        year, month = ym
        if (year > cutoff_year) or (year == cutoff_year and month >= cutoff_month):
            filtered.append(url)
    return filtered


def load_existing_games(out_path: Path) -> set[str]:
    """Load existing game URLs from PGN file to avoid duplicates."""
    existing_urls = set()
    if not out_path.exists():
        return existing_urls

    try:
        with out_path.open("r", encoding="utf-8") as f:
            current_pgn = []
            for line in f:
                line = line.rstrip()
                if line:
                    current_pgn.append(line)
                elif current_pgn:
                    # End of a PGN block
                    pgn_text = "\n".join(current_pgn)
                    url = extract_game_url(pgn_text)
                    if url:
                        existing_urls.add(url)
                    current_pgn = []
            
            # Handle last PGN if file doesn't end with blank line
            if current_pgn:
                pgn_text = "\n".join(current_pgn)
                url = extract_game_url(pgn_text)
                if url:
                    existing_urls.add(url)
    except Exception as e:
        print(f"Warning: Could not read existing file: {e}")
        return set()

    print(f"Found {len(existing_urls)} existing games")
    return existing_urls


def download_all_pgn(username: str, out_path: Path, fetch_all: bool = False, polite_sleep_s: float = 0.2) -> None:
    out_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Find the most recent game timestamp for incremental downloads
    cutoff_timestamp = None if fetch_all else find_most_recent_timestamp(out_path)
    
    # Load existing games to avoid duplicates
    existing_urls = load_existing_games(out_path)
    new_games = 0
    skipped_games = 0
    too_old_games = 0

    with requests.Session() as s:
        s.headers.update({"User-Agent": "chesscom-archive-downloader/1.0"})
        archives_url = API.format(username=username)
        archives = get_json(s, archives_url)["archives"]
        original_archives_count = len(archives)
        archives = filter_archives_by_cutoff(archives, cutoff_timestamp)
        if cutoff_timestamp:
            cutoff_dt = datetime.fromtimestamp(cutoff_timestamp, timezone.utc)
            skipped_months = original_archives_count - len(archives)
            print(f"Filtering archives to {cutoff_dt.strftime('%Y-%m')} and newer")
            if skipped_months > 0:
                print(f"Skipped {skipped_months} archive months older than cutoff")

        with out_path.open("a", encoding="utf-8", newline="\n") as f:
            total_months = len(archives)
            for i, month_url in enumerate(archives, 1):
                print(f"[{i}/{total_months}] {month_url}")
                month = get_json(s, month_url)
                for g in month.get("games", []):
                    pgn = g.get("pgn")
                    if not pgn:
                        continue
                    
                    # Check if game is too old (only if cutoff_timestamp is set)
                    if cutoff_timestamp:
                        game_timestamp = extract_game_timestamp(pgn)
                        if game_timestamp and game_timestamp <= cutoff_timestamp:
                            too_old_games += 1
                            continue
                    
                    # Check for duplicates
                    game_url = g.get("url")
                    if game_url and game_url in existing_urls:
                        skipped_games += 1
                        continue
                    
                    f.write(pgn)
                    f.write("\n\n")
                    new_games += 1
                    if game_url:
                        existing_urls.add(game_url)
                
                time.sleep(polite_sleep_s)

    print(f"\nDone -> {out_path}")
    print(f"New games added: {new_games}")
    if skipped_games > 0:
        print(f"Duplicates skipped: {skipped_games}")
    if too_old_games > 0:
        print(f"Older games skipped: {too_old_games}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download chess.com games as PGN. By default, only fetches games newer than the most recent game already downloaded."
    )
    parser.add_argument(
        "--username",
        default="rtreit",
        help="Chess.com username (default: rtreit)"
    )
    parser.add_argument(
        "--fetch-all",
        action="store_true",
        help="Fetch all games regardless of timestamp (default: only fetch new games)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="Output file path (default: chesscom_<username>.pgn)"
    )
    
    args = parser.parse_args()
    
    username = args.username
    out_file = args.output or Path(f"chesscom_{username}.pgn")
    
    if args.fetch_all:
        print("Fetching all games (timestamp filtering disabled)")
    else:
        print("Fetching only new games (incremental mode)")
    
    download_all_pgn(username, out_file, fetch_all=args.fetch_all)
