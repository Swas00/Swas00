"""Shared GitHub data helpers (stdlib only)."""
import json
import os
import urllib.request

QUERY = """query($login:String!){user(login:$login){
 createdAt followers{totalCount} following{totalCount}
 contributionsCollection{totalCommitContributions totalPullRequestContributions
  totalIssueContributions restrictedContributionsCount
  contributionCalendar{totalContributions weeks{contributionDays{date contributionCount}}}}}}"""


def _req(url, data=None):
    h = {"User-Agent": "profile-gen", "Accept": "application/vnd.github+json"}
    tok = os.environ.get("GITHUB_TOKEN")
    if tok:
        h["Authorization"] = f"Bearer {tok}"
    r = urllib.request.Request(url, data=data, headers=h)
    with urllib.request.urlopen(r, timeout=30) as f:
        return f.read()


def _preview_graph(login):
    """Offline stand-in for local design previews only (PREVIEW_DATA=1, no token).
    Deterministic fake contribution calendar so layouts can be checked without credentials.
    The scheduled workflow always has a token and never takes this path."""
    import random
    from datetime import date, timedelta
    rnd = random.Random(login)
    end = date.today()
    start = end - timedelta(days=363)
    start -= timedelta(days=(start.weekday() + 1) % 7)  # back to Sunday
    days_, d = [], start
    while d <= end:
        base = 0.55 if d.weekday() < 5 else 0.3
        burst = 2.4 if (d.toordinal() // 17) % 4 == 0 else 1.0
        c = 0 if rnd.random() > base * burst else int(rnd.expovariate(1 / 3.2) * burst) + 1
        days_.append((d.isoformat(), c if d <= end else 0))
        d += timedelta(days=1)
    weeks = [{"contributionDays": [{"date": a, "contributionCount": b} for a, b in days_[i:i + 7]]}
             for i in range(0, len(days_), 7)]
    tot = sum(b for _, b in days_)
    return {"createdAt": "2023-01-01T00:00:00Z", "followers": {"totalCount": 0}, "following": {"totalCount": 0},
            "contributionsCollection": {"totalCommitContributions": tot, "totalPullRequestContributions": 0,
                                        "totalIssueContributions": 0, "restrictedContributionsCount": 0,
                                        "contributionCalendar": {"totalContributions": tot, "weeks": weeks}}}


def user_graph(login):
    if not os.environ.get("GITHUB_TOKEN") and os.environ.get("PREVIEW_DATA") == "1":
        return _preview_graph(login)
    body = json.dumps({"query": QUERY, "variables": {"login": login}}).encode()
    out = json.loads(_req("https://api.github.com/graphql", body))
    if "errors" in out:
        raise SystemExit(f"graphql: {out['errors']}")
    return out["data"]["user"]


def days(user):
    """Flat chronological list of (date, count)."""
    wk = user["contributionsCollection"]["contributionCalendar"]["weeks"]
    return [(d["date"], d["contributionCount"]) for w in wk for d in w["contributionDays"]]


def streaks(ds):
    """(current, longest). Today with 0 contributions does not break a streak."""
    longest = run = 0
    for _, c in ds:
        run = run + 1 if c else 0
        longest = max(longest, run)
    cur = 0
    for i, (_, c) in enumerate(reversed(ds)):
        if c:
            cur += 1
        elif i != 0:
            break
    return cur, longest


def repos(login):
    out, page = [], 1
    while True:
        b = json.loads(_req(f"https://api.github.com/users/{login}/repos?per_page=100&page={page}"))
        out += b
        if len(b) < 100:
            return [r for r in out if not r["fork"]]
        page += 1


def push_hours(login, tz_minutes=330, pages=3):
    """(hist24, n): pushes per local hour from the public events feed (last ~90 days)."""
    from datetime import datetime, timedelta
    hist, n = [0] * 24, 0
    for p in range(1, pages + 1):
        try:
            evs = json.loads(_req(f"https://api.github.com/users/{login}/events/public?per_page=100&page={p}"))
        except Exception:
            break
        for e in evs:
            if e.get("type") == "PushEvent":
                d = datetime.fromisoformat(e["created_at"].replace("Z", "+00:00")) + timedelta(minutes=tz_minutes)
                hist[d.hour] += 1
                n += 1
        if not evs:
            break  # pages can be short (filtered); only an empty page ends the feed
    return hist, n


def push_events(login, pages=3):
    """[(repo_name, datetime_utc)] for PushEvents in the public feed (~300 events max)."""
    from datetime import datetime
    out = []
    for p in range(1, pages + 1):
        try:
            evs = json.loads(_req(f"https://api.github.com/users/{login}/events/public?per_page=100&page={p}"))
        except Exception:
            break
        if not evs:
            break
        for e in evs:
            if e.get("type") == "PushEvent":
                name = e["repo"]["name"].split("/", 1)[-1]
                out.append((name, datetime.fromisoformat(e["created_at"].replace("Z", "+00:00"))))
    return out
