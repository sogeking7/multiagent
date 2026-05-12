"""Build samples.json from inline triple-quoted snippets.

This avoids manual JSON-escaping of multi-line Python code. The flaws in each
snippet were chosen to be (a) realistic — code a working engineer might
actually commit — and (b) subtle enough that a non-expert reviewer could miss
at least one. Each sample is ~12-30 lines of Python.

Run: python build_samples.py
"""

from __future__ import annotations

import json
from pathlib import Path
from textwrap import dedent


def sample(sample_id: str, category: str, code: str, known_issues: list[str]) -> dict:
    return {
        "id": sample_id,
        "category": category,
        "code": dedent(code).strip("\n"),
        "known_issues": known_issues,
    }


SAMPLES: list[dict] = []


# ---------------------------------------------------------------------------
# Category 1: Logic bugs (L1-L10)
# ---------------------------------------------------------------------------

SAMPLES.append(sample(
    "L1", "logic",
    """
    from typing import Iterable, List, TypeVar

    T = TypeVar("T")


    def paginate(items: List[T], page: int, page_size: int) -> List[T]:
        \"\"\"Return the items belonging to the requested 1-indexed page.\"\"\"
        start = page * page_size
        end = start + page_size
        return items[start:end]


    def page_count(items: Iterable[T], page_size: int) -> int:
        return (len(list(items)) + page_size - 1) // page_size
    """,
    [
        "Off-by-one in paginate: start should be (page - 1) * page_size for 1-indexed pages; current code skips the first page entirely (page=1 returns items[size:2*size]).",
    ],
))

SAMPLES.append(sample(
    "L2", "logic",
    """
    from typing import List


    def moving_average(values: List[float], window: int) -> List[float]:
        \"\"\"Return the moving average of `values` over a fixed window size.\"\"\"
        if window <= 0:
            raise ValueError("window must be positive")
        if window > len(values):
            return []
        result: List[float] = []
        for i in range(len(values) - window):
            window_slice = values[i:i + window]
            result.append(sum(window_slice) / window)
        return result
    """,
    [
        "Off-by-one in the loop bound: range(len(values) - window) skips the final window; should be range(len(values) - window + 1).",
    ],
))

SAMPLES.append(sample(
    "L3", "logic",
    """
    from typing import List


    def median(numbers: List[float]) -> float:
        \"\"\"Return the median of a numeric list.\"\"\"
        sorted_nums = sorted(numbers)
        n = len(sorted_nums)
        if n % 2 == 0:
            return (sorted_nums[n // 2 - 1] + sorted_nums[n // 2]) / 2
        return sorted_nums[n // 2]


    def summarize(numbers: List[float]) -> dict:
        return {"min": min(numbers), "max": max(numbers), "median": median(numbers)}
    """,
    [
        "No handling for empty input: median([]) raises IndexError instead of returning None or raising a meaningful error.",
        "summarize() also fails on empty input via min/max; the empty-list case is not propagated cleanly.",
    ],
))

SAMPLES.append(sample(
    "L4", "logic",
    """
    import time
    from typing import List


    def append_log(message: str, history: List[dict] = []) -> List[dict]:
        \"\"\"Append a message to a history list and return the updated list.\"\"\"
        history.append({"msg": message, "ts": time.time()})
        return history


    def reset_log() -> List[dict]:
        # Reset by handing back a new list; callers should use this.
        return []


    def latest_messages(history: List[dict], n: int = 5) -> List[dict]:
        return history[-n:]
    """,
    [
        "Mutable default argument: history=[] is shared across all calls that omit the argument, causing state to leak between unrelated callers.",
    ],
))

SAMPLES.append(sample(
    "L5", "logic",
    """
    def average_grade(grades):
        \"\"\"Return the arithmetic mean of a list of numeric grades.\"\"\"
        total = 0
        count = 0
        for g in grades:
            total += g
            count += 1
        if count == 0:
            return 0
        return total // count
    """,
    [
        "Uses integer floor division (//) where true mean is expected; for grades like [85, 92, 78] this returns 85 instead of 85.0.",
    ],
))

SAMPLES.append(sample(
    "L6", "logic",
    """
    def make_event_handlers(event_names):
        \"\"\"Return a list of callables, one per event name.\"\"\"
        handlers = []
        for name in event_names:
            handlers.append(lambda: print(f"handling {name}"))
        return handlers


    if __name__ == "__main__":
        for h in make_event_handlers(["click", "hover", "drag"]):
            h()
    """,
    [
        "Late-binding closure: every lambda captures the variable `name`, not its value, so all handlers print the last event in the list (\"drag\").",
    ],
))

SAMPLES.append(sample(
    "L7", "logic",
    """
    def can_edit_post(user, post):
        \"\"\"Return True iff `user` is permitted to edit `post`.\"\"\"
        if user.is_admin:
            return True
        if post.author_id == user.id:
            return True
        # Allow editors of equal or higher rank to moderate.
        if user.role_level <= post.required_level:
            return True
        return False
    """,
    [
        "Inverted comparison: `user.role_level <= post.required_level` lets LOWER-privileged users edit; should be `>=`. This is a privilege-escalation bug.",
    ],
))

SAMPLES.append(sample(
    "L8", "logic",
    """
    def factorial(n: int) -> int:
        \"\"\"Return n! for non-negative integer n.\"\"\"
        if n == 1:
            return 1
        return n * factorial(n - 1)


    def n_choose_k(n: int, k: int) -> int:
        \"\"\"Return the binomial coefficient C(n, k).\"\"\"
        if k < 0 or k > n:
            return 0
        return factorial(n) // (factorial(k) * factorial(n - k))


    def permutations(n: int, k: int) -> int:
        return factorial(n) // factorial(n - k)
    """,
    [
        "Missing base case for n == 0: factorial(0) recurses into negative arguments and overflows the stack. n_choose_k(n, 0) / n_choose_k(n, n) / permutations(n, n) therefore crash.",
    ],
))

SAMPLES.append(sample(
    "L9", "logic",
    """
    def parse_csv_line(line):
        \"\"\"Parse a single CSV line into a list of cell strings.\"\"\"
        parts = line.split(",")
        cleaned = []
        for p in parts:
            p = p.strip()
            if p.startswith('"') and p.endswith('"'):
                p = p[1:-1]
            cleaned.append(p)
        return cleaned
    """,
    [
        "Naive split on ',' breaks on quoted fields containing commas (e.g. 'a,\"b,c\",d' yields 4 cells instead of 3); a CSV parser or a proper state machine is needed.",
    ],
))

SAMPLES.append(sample(
    "L10", "logic",
    """
    from typing import List


    def is_paid_in_full(amount_paid: float, total_due: float) -> bool:
        \"\"\"Return True if the customer has paid exactly the amount owed.\"\"\"
        return amount_paid == total_due


    def remaining_balance(amount_paid: float, total_due: float) -> float:
        if is_paid_in_full(amount_paid, total_due):
            return 0.0
        return total_due - amount_paid


    def settle_invoices(invoices: List[dict]) -> List[dict]:
        result = []
        for inv in invoices:
            inv["balance"] = remaining_balance(inv["paid"], inv["due"])
            inv["closed"] = is_paid_in_full(inv["paid"], inv["due"])
            result.append(inv)
        return result
    """,
    [
        "Direct float equality in is_paid_in_full: financial sums computed from prior arithmetic rarely hit exact equality (e.g. 0.1 + 0.2 != 0.3). Should compare with a tolerance or use Decimal — this flows into settle_invoices marking invoices as un-closed even when they are paid in full.",
    ],
))


# ---------------------------------------------------------------------------
# Category 2: Security issues (S1-S10)
# ---------------------------------------------------------------------------

SAMPLES.append(sample(
    "S1", "security",
    """
    import sqlite3
    from typing import Optional, Tuple


    def get_user_by_username(
        conn: sqlite3.Connection, username: str
    ) -> Optional[Tuple[int, str, str]]:
        \"\"\"Look up a user by username and return (id, email, role).\"\"\"
        cursor = conn.cursor()
        query = f"SELECT id, email, role FROM users WHERE username = '{username}'"
        cursor.execute(query)
        return cursor.fetchone()


    def authenticate(conn: sqlite3.Connection, username: str, _password: str) -> bool:
        return get_user_by_username(conn, username) is not None
    """,
    [
        "SQL injection via f-string interpolation of `username` into the query. Must use parameterized queries (e.g. cursor.execute(\"... WHERE username = ?\", (username,))). The authenticate() wrapper inherits the same vulnerability.",
    ],
))

SAMPLES.append(sample(
    "S2", "security",
    """
    import psycopg2


    def connect_to_production_db():
        \"\"\"Return a connection to the production users database.\"\"\"
        return psycopg2.connect(
            host="prod-db.internal.example.com",
            port=5432,
            user="admin",
            password="P@ssw0rd2024!",
            database="users",
            sslmode="require",
        )
    """,
    [
        "Hardcoded production credentials (user 'admin', password 'P@ssw0rd2024!') in source. Secrets must come from environment variables or a secret manager; committing them to a repo leaks them permanently via git history.",
    ],
))

SAMPLES.append(sample(
    "S3", "security",
    """
    import pickle


    def load_user_session(session_blob: bytes):
        \"\"\"Restore a user session previously serialized with `pickle.dumps`.\"\"\"
        return pickle.loads(session_blob)


    def restore_from_request(request):
        cookie = request.cookies.get("session")
        if cookie is None:
            return None
        return load_user_session(bytes.fromhex(cookie))
    """,
    [
        "Insecure deserialization: pickle.loads on attacker-controlled data (a cookie value) allows arbitrary code execution via __reduce__. Use a signed JSON token or itsdangerous instead.",
    ],
))

SAMPLES.append(sample(
    "S4", "security",
    """
    from pathlib import Path


    USER_DATA_ROOT = "/var/data/users"


    def read_user_file(username: str, filename: str) -> bytes:
        path = f"{USER_DATA_ROOT}/{username}/{filename}"
        with open(path, "rb") as f:
            return f.read()
    """,
    [
        "Path traversal: `filename='../../../etc/passwd'` escapes USER_DATA_ROOT. Must resolve and verify the path is contained within USER_DATA_ROOT (e.g. Path(USER_DATA_ROOT).resolve() then check is_relative_to).",
    ],
))

SAMPLES.append(sample(
    "S5", "security",
    """
    import random
    import string
    import time


    def generate_password_reset_token(length: int = 32) -> str:
        \"\"\"Generate a single-use token to email to the user.\"\"\"
        random.seed(int(time.time()))
        alphabet = string.ascii_letters + string.digits
        return "".join(random.choice(alphabet) for _ in range(length))


    def send_reset_email(user_email: str) -> str:
        token = generate_password_reset_token()
        # Pretend to email the token to the user.
        return token
    """,
    [
        "Uses `random` (Mersenne Twister, predictable from a few observed outputs) for a security-sensitive token. Must use `secrets.token_urlsafe` or `secrets.choice` from the `secrets` module.",
        "Seeding random with `int(time.time())` makes the token even more predictable — an attacker who knows the approximate request time can enumerate the seed space.",
    ],
))

SAMPLES.append(sample(
    "S6", "security",
    """
    import subprocess
    from typing import List


    def get_file_info(filename: str) -> str:
        \"\"\"Return the output of `stat` for the given file.\"\"\"
        result = subprocess.check_output(
            f"stat {filename}", shell=True, text=True
        )
        return result


    def batch_file_info(filenames: List[str]) -> List[str]:
        return [get_file_info(f) for f in filenames]
    """,
    [
        "Command injection: `shell=True` with an f-string lets a filename like 'foo; rm -rf /' execute arbitrary shell. Must pass a list of args and shell=False (e.g. ['stat', filename]). batch_file_info inherits this vulnerability across every input.",
    ],
))

SAMPLES.append(sample(
    "S7", "security",
    """
    from typing import List


    def render_comment(comment_text: str, author_name: str) -> str:
        \"\"\"Render a user's comment for inclusion in an HTML page.\"\"\"
        return (
            f"<div class='comment'>"
            f"<strong>{author_name}</strong>: "
            f"<span>{comment_text}</span>"
            f"</div>"
        )


    def render_comment_thread(comments: List[dict]) -> str:
        return "\\n".join(
            render_comment(c["text"], c["author"]) for c in comments
        )
    """,
    [
        "Stored XSS: user-controlled `comment_text` and `author_name` are interpolated raw into HTML. Must HTML-escape (html.escape) or use a templating engine with auto-escape. render_comment_thread amplifies the vulnerability across every comment.",
    ],
))

SAMPLES.append(sample(
    "S8", "security",
    """
    import hashlib


    def hash_password(password: str) -> str:
        \"\"\"Hash a password for storage.\"\"\"
        return hashlib.md5(password.encode("utf-8")).hexdigest()


    def verify_password(password: str, stored_hash: str) -> bool:
        return hash_password(password) == stored_hash
    """,
    [
        "MD5 (and any fast, unsalted hash) is unsuitable for passwords: rainbow-table lookups, GPU brute-force, no per-user salt. Use a slow KDF like bcrypt, scrypt, or argon2 with a unique salt.",
        "verify_password uses '==' (non-constant-time comparison), enabling timing attacks; should use hmac.compare_digest.",
    ],
))

SAMPLES.append(sample(
    "S9", "security",
    """
    import requests


    def fetch_user_avatar(image_url: str) -> bytes:
        \"\"\"Download a user-supplied avatar URL and return the image bytes.\"\"\"
        response = requests.get(image_url, timeout=5)
        response.raise_for_status()
        return response.content


    def save_avatar_for(user_id: int, image_url: str, store) -> None:
        data = fetch_user_avatar(image_url)
        store.put(f"avatars/{user_id}.png", data)
    """,
    [
        "Server-Side Request Forgery (SSRF): unvalidated user-supplied URL can be pointed at internal services (http://169.254.169.254/, http://localhost:8080/admin). Must validate scheme/host and block private/loopback/link-local ranges.",
        "No content-type or size limit: a malicious URL can return arbitrary bytes (e.g. multi-GB) that the store then persists under a .png extension.",
    ],
))

SAMPLES.append(sample(
    "S10", "security",
    """
    from typing import Any


    def calculate(expression: str) -> Any:
        \"\"\"Evaluate a simple arithmetic expression like '2 + 2 * 3'.\"\"\"
        return eval(expression)


    def handle_calc_request(form) -> dict:
        expr = form.get("expr", "0")
        return {"result": calculate(expr)}


    def batch_calculate(expressions):
        return [calculate(e) for e in expressions]
    """,
    [
        "eval() on user-supplied input is remote code execution: `__import__('os').system('rm -rf /')` is a valid Python expression. Use `ast.literal_eval` or a real expression parser. handle_calc_request and batch_calculate both expose this RCE through any caller-provided expression.",
    ],
))


# ---------------------------------------------------------------------------
# Category 3: Style / maintainability (ST1-ST10)
# ---------------------------------------------------------------------------

SAMPLES.append(sample(
    "ST1", "style",
    """
    def process_order(order):
        if order:
            if order.items:
                total = 0
                for item in order.items:
                    if item.in_stock:
                        if item.discount:
                            if item.discount.valid:
                                total += item.price * (1 - item.discount.amount)
                            else:
                                total += item.price
                        else:
                            total += item.price
                    else:
                        return None
                return total
            else:
                return 0
        else:
            return None
    """,
    [
        "Deep nesting (5 levels) makes the control flow hard to follow; should be flattened via early returns or guard clauses.",
        "Multiple semantically-overloaded return values (None means 'no order' AND 'out of stock'); a caller cannot distinguish them. Raise specific exceptions or return a result object.",
    ],
))

SAMPLES.append(sample(
    "ST2", "style",
    """
    import json


    def read_config(path):
        with open(path) as f:
            data = json.loads(f.read())
        return data["api_key"], data["endpoint"], data["timeout"]


    def main():
        api_key, endpoint, timeout = read_config("config.json")
        print(f"Connecting to {endpoint}...")
    """,
    [
        "No error handling: read_config crashes opaquely on FileNotFoundError, JSONDecodeError, or KeyError. Should catch and re-raise with context, or return a typed Result.",
        "Returning a 3-tuple is positional-fragile; reordering or adding a field silently breaks every caller. A dataclass or TypedDict would be safer.",
    ],
))

SAMPLES.append(sample(
    "ST3", "style",
    """
    def calc_tax(p, q, r):
        if r == "US":
            return p * q * 0.07
        elif r == "EU":
            return p * q * 0.20
        elif r == "JP":
            return p * q * 0.10
        return p * q * 0.0


    def total_with_tax(p, q, r):
        return p * q + calc_tax(p, q, r)
    """,
    [
        "Single-letter parameter names (p, q, r) for business-domain values obscure intent; should be price, quantity, region.",
        "Magic numbers (0.07, 0.20, 0.10) for tax rates should be named constants or a lookup table indexed by region.",
    ],
))

SAMPLES.append(sample(
    "ST4", "style",
    """
    def check_password_strength(password: str) -> str:
        \"\"\"Return a coarse-grained strength label for a password.\"\"\"
        if len(password) < 8:
            return "weak"
        if len(password) < 12:
            return "medium"
        if len(password) < 16:
            return "strong"
        return "very strong"


    def is_password_acceptable(password: str) -> bool:
        return check_password_strength(password) in ("strong", "very strong")
    """,
    [
        "Strength is judged on length alone; ignores character-class diversity (digits, symbols, mixed case), common-password lists, and entropy — the standard guidance from NIST SP 800-63B.",
        "Magic numbers (8, 12, 16) and string return values ('weak', 'medium', ...) should be named constants or an Enum; is_password_acceptable is fragile to a future rename of a label string.",
    ],
))

SAMPLES.append(sample(
    "ST5", "style",
    """
    def transfer_money(from_account, to_account, amount):
        \"\"\"Move `amount` from one account to another and record the transfer.\"\"\"
        from_account.balance -= amount
        to_account.balance += amount
        log_transfer(from_account.id, to_account.id, amount)
        return True


    def bulk_transfer(transfers):
        \"\"\"Process a list of (src, dst, amount) tuples in order.\"\"\"
        results = []
        for src, dst, amount in transfers:
            results.append(transfer_money(src, dst, amount))
        return results
    """,
    [
        "No input validation: negative amounts, same source and destination, insufficient balance, or None accounts are all silently accepted.",
        "Not atomic: the two balance writes are not wrapped in a transaction, so a crash between them leaves money missing. log_transfer is also outside any transaction.",
        "bulk_transfer has no per-item error isolation: a failure mid-list leaves some transfers applied and others not, with no rollback.",
    ],
))

SAMPLES.append(sample(
    "ST6", "style",
    """
    def render_user_card(user):
        html = "<div class='card'>"
        html += f"<h2>{user.name}</h2>"
        html += f"<p>{user.bio}</p>"
        html += "</div>"
        return html


    def render_post_card(post):
        html = "<div class='card'>"
        html += f"<h2>{post.title}</h2>"
        html += f"<p>{post.summary}</p>"
        html += "</div>"
        return html


    def render_product_card(product):
        html = "<div class='card'>"
        html += f"<h2>{product.name}</h2>"
        html += f"<p>{product.description}</p>"
        html += "</div>"
        return html
    """,
    [
        "DRY violation: three near-identical functions that differ only in which attributes they pull. Should be one helper taking title and body strings, or a template-based renderer.",
    ],
))

SAMPLES.append(sample(
    "ST7", "style",
    """
    import hashlib


    def handle_signup(form_data, db, mailer):
        if not form_data.get("email") or "@" not in form_data["email"]:
            return {"error": "Invalid email"}
        if len(form_data.get("password", "")) < 8:
            return {"error": "Password too short"}
        user = User(email=form_data["email"])
        user.password_hash = hashlib.sha256(form_data["password"].encode()).hexdigest()
        db.session.add(user)
        db.session.commit()
        mailer.send(user.email, "Welcome!", "Thanks for signing up")
        log_signup(user.id)
        return {"user_id": user.id}
    """,
    [
        "Single function handles validation, hashing, persistence, email, and logging — five responsibilities that should be separated for testability and to allow each step to fail/retry independently.",
        "SHA-256 (unsalted, fast) used for password hashing — see also the security-category critique; mention here for maintainability since the hashing strategy is buried inside an HTTP handler.",
    ],
))

SAMPLES.append(sample(
    "ST8", "style",
    """
    def safe_divide(a, b):
        try:
            return a / b
        except:
            return 0


    def average(values):
        try:
            return safe_divide(sum(values), len(values))
        except:
            return 0
    """,
    [
        "Bare `except:` swallows everything, including KeyboardInterrupt and SystemExit; should catch the specific exception (ZeroDivisionError) or at least `except Exception`.",
        "Silently returning 0 on error hides bugs; the caller cannot distinguish 'real zero' from 'something went wrong'.",
    ],
))

SAMPLES.append(sample(
    "ST9", "style",
    """
    _cache = {}


    def get_user_data(user_id):
        if user_id in _cache:
            return _cache[user_id]
        data = fetch_from_db(user_id)
        _cache[user_id] = data
        return data


    def update_user(user_id, new_data):
        save_to_db(user_id, new_data)
    """,
    [
        "Mutable module-level cache with no invalidation: update_user writes to the DB but does not evict _cache[user_id], so subsequent reads return stale data.",
        "Cache has no bound, no TTL, and is not thread-safe; should use functools.lru_cache, a TTL cache, or an explicit cache class.",
    ],
))

SAMPLES.append(sample(
    "ST10", "style",
    """
    def find_user(user_id, db):
        if user_id < 0:
            return False
        user = db.query(User).filter_by(id=user_id).first()
        if user:
            return user
        return None


    def display_name(user_id, db):
        u = find_user(user_id, db)
        if u:
            return u.name
        return "Unknown"
    """,
    [
        "find_user returns three different types (User, False, None) depending on path; callers must remember which sentinel means what. Should consistently return Optional[User] and raise for invalid input.",
    ],
))


def main():
    assert len(SAMPLES) == 30, f"expected 30 samples, got {len(SAMPLES)}"
    out_path = Path(__file__).parent / "samples.json"
    with out_path.open("w") as f:
        json.dump(SAMPLES, f, indent=2)
    print(f"Wrote {len(SAMPLES)} samples to {out_path}")
    by_cat: dict[str, int] = {}
    for s in SAMPLES:
        by_cat[s["category"]] = by_cat.get(s["category"], 0) + 1
    print("By category:", by_cat)
    # Sanity check: every snippet between 10 and 40 lines (prompt requirement).
    for s in SAMPLES:
        n = len(s["code"].splitlines())
        if not (10 <= n <= 40):
            raise SystemExit(f"sample {s['id']} has {n} lines (out of [10, 40])")
    print("All snippets within line bounds (10-40).")


if __name__ == "__main__":
    main()
