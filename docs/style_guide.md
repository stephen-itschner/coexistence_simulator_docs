# Python Style Guide

> **Scope** This document codifies layout, naming, typing, documentation, and
> error‑handling conventions for all Python projects in the project.
> Automation enforces every MUST; reviewers catch the rest.

---

## 1. Layout & Formatting

### 1.1 Indentation and Whitespace
| Item                | Rule                                                       |
|---------------------|------------------------------------------------------------|
| Indentation         | **4 spaces** exactly or tab                                |
| Continuation align  | Hanging indent one level beyond the opening delimiter.     |
| Trailing whitespace | Strip on save; CI fails if any remain.                     |
| Final newline       | End every text file with **one** newline—no more, no less. |



### 1.2 Line Length
*Soft limit 88 chars* (Black default), *hard limit 100* (CI enforced by Ruff).  
Long URLs/imports may overflow; avoid mid‑string backslashes.

```python
# ✓ good
result = (
    first_component.long_attribute_name
    + second_component.even_longer_attribute
    - delta
)

# ✗ bad
if some_really_long_condition and another_condition and third_condition: ...
```

### 1.3 File Structure
1. `__future__` imports.  
2. Standard‑library imports.  
3. Third‑party imports.  
4. Local package imports.  
5. Constants & type aliases.  
6. Public class/function definitions.

Separate each group with **one** blank line.

```python
from __future__ import annotations

import json
import logging
from pathlib import Path

import httpx

from .constants import CACHE_TTL
```

### 1.4 Blank‑Line Conventions
* Two blank lines before any *top‑level* `class` or `def`.
* One blank line between methods inside a class.
* No blank line after an `if TYPE_CHECKING:` block.

### 1.5 Encoding Declaration

### 1.6 ASCII‑only Characters
| Purpose         | Rule                                                                                         |
|-----------------|----------------------------------------------------------------------------------------------|
| General code    | Restrict source files to **plain ASCII** that can be typed on a standard U.S. keyboard.      |
| Degree symbol   | Write `deg` or include units in words (`temperature_celsius`)—never `°`.                     |
| Exponents       | Use caret notation (`^2`, `x**2`)—never superscript `²`.                                      |
| Dashes / rules  | For visual separators in comments, use `----` or `# ----`—keep out en/em dashes (`–`, `—`).   |
| Ellipsis        | Type three periods `...`—never the single‑character ellipsis `…`.                            |
| Arrows & icons  | Use ASCII equivalents (`->`, `<-`, `=>`)—avoid `→`, `⇐`, `✓`, etc.                           |
| Exceptions      | **User‑facing strings** or **Unicode test fixtures** may contain non‑ASCII when essential.   |

> *Why?* Mixed Unicode confuses diff tools and some terminals; ASCII guarantees
> portability and prevents copy‑paste artefacts.

```python
# ✓ good
temp_str = f"{temperature_degC:.1f} deg C"

# ✗ bad
temp_str = f"{temperature_degC:.1f} °C"

# ✓ section break
# ---- Data processing ----

# ✗ section break
# ——— Data processing ———
```

CI enforces this rule via `ruff check --select UP017` (for Unicode identifiers)
and a custom script banning non‑ASCII outside sanctioned locations.
### 1.5 Encoding Declaration
Add `# -*- coding: utf-8 -*-` only for Python ≤ 3.6.  
Modern code omits it.

---

## 2. Naming Conventions

| Entity             | Style              | Example                     |
|--------------------|--------------------|-----------------------------|
| Package / module   | `lowercase_snake`  | `network_utils`             |
| Class / Exception  | `CapWords`         | `CsvReader`, `ParserError`  |
| Function / Method  | `snake_case`       | `parse_headers`             |
| Constant           | `UPPER_SNAKE`      | `MAX_CHUNK_SIZE`            |
| Type Alias         | `CapWords` + suffix| `JsonDict`, `BytesLike`     |
| Private attribute  | `_leading_underscore` | `_buffer`, `_validate`   |
| Magic dunder       | `__dunder__`       | `__all__`, `__slots__`      |

* Treat acronyms like ordinary words in `CapWords`: `HttpServer`, `IdToken`.
* Boolean variables start with verbs: `is_valid`, `has_errors`, `should_retry`.
* Ban Hungarian notation and cryptic two‑letter names (except `i`, `j`, `x`, `y`).

---

## 3. Typing & Static Analysis

### 3.1 Baseline Rules
1. Every *public* function must have type hints.  
2. Enable `from __future__ import annotations` in all modules.  
3. Run `mypy --strict` (or Pyright strict) in CI; zero new errors permitted.  
4. Never use mutable default arguments.

### 3.2 Preferred Abstractions
* Accept abstract collections (`Sequence`, `Mapping`) for read‑only params.  
* Return the narrowest useful concrete type.  
* Backport bleeding‑edge features via `typing_extensions` (`Self`, `TypeAlias`).

```python
from collections.abc import Mapping, Sequence
from typing import Self

class Vector:
    def __init__(self, xs: Sequence[float]) -> None:
        self._xs = tuple(xs)

    def scale(self, factor: float) -> Self:
        return Vector(x * factor for x in self._xs)
```

### 3.3 Type‑Guarded Imports
```python
from typing import TYPE_CHECKING

if TYPE_CHECKING:  # skipped at runtime
    from Crypto.Cipher import AES
```

### 3.4 Runtime Validation
Rely on runtime validators (`pydantic.validate_call`, `beartype`) at API
boundaries—*never* on `assert`, which disappears under `python -O`.

---

## 4. Documentation

### 4.1 Docstring Format (Google Style)
```python
def backoff(attempt: int, *, base: float = 2.0) -> float:
    """Compute exponential back‑off delay.

    Args:
        attempt: Zero‑based retry index.
        base: Multiplier applied to the exponent.

    Returns:
        Seconds to sleep before the next retry.

    Raises:
        ValueError: If `attempt` is negative.
    """
    if attempt < 0:
        raise ValueError("attempt must be ≥ 0")
    return base ** attempt
```

### 4.2 Module‑Level Docstrings
* One‑line summary sentence.  
* Paragraphs describing purpose, usage, and links.  
* Enumerate major public symbols.

### 4.3 Inline Comments
Explain *why*, not *what*; keep within 88 chars.

```python
# Upstream sometimes drops TLS connections after 59 s; we retry idempotent
# requests on ECONNRESET to mask the hiccup.
```

---

## 5. Error Handling & Logging

### 5.1 Exception Hierarchy
```python
class BaseError(Exception):
    """Root of all project exceptions."""

class ParseError(BaseError):
    """Raised when input cannot be parsed."""
```

### 5.2 Catching Policy
| Context                   | Action                                   |
|---------------------------|------------------------------------------|
| Library code              | Let exceptions propagate.                |
| CLI entry point           | Catch, log, return `sys.exit(1)`.        |
| Long‑running service loop | Catch, log, continue when safe.          |

### 5.3 Logging Setup
```python
import logging
import structlog

logging.basicConfig(
    format="%(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler()],
)
structlog.configure(
    processors=[
        structlog.processors.add_timestamp,
        structlog.processors.JSONRenderer(),
    ],
    wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
)
logger = structlog.get_logger(__name__)
```

* Default level `INFO` in prod; `DEBUG` in tests (`pytest -o log_cli=true`).
* Use JSON renderer in production; console renderer for local dev.
* Redact secrets (`[REDACTED]`).

### 5.4 Never Silence Exceptions
```python
# ✓ good
try:
    payload = json.loads(raw)
except json.JSONDecodeError as exc:
    raise ParseError("invalid JSON") from exc

# ✗ bad
except Exception:
    pass
```

### 5.5 Retry Strategy
Use `tenacity`:
```python
from tenacity import retry, stop_after_attempt, wait_exponential_jitter

@retry(stop=stop_after_attempt(5), wait=wait_exponential_jitter(1, 10))
def fetch(url: str) -> bytes:
    ...
```

### 5.6 CI Guards
* `ruff check --select BLE,B902` forbids bare or broad excepts.  
* `pytest tests/test_logging.py` guards log schema.

---

## 6. Dependency Management (Conda‑first)

Our projects run in **Conda** environments described by an
`environment.yml` file checked into the repository root.

### 6.1 Creating the Environment
```bash
# one‑time bootstrap
conda env create -f environment.yml
# or, for speed
mamba env create -f environment.yml

# later updates
conda env update -f environment.yml --prune
```
*Never* install directly into the *base* environment.

### 6.2 `environment.yml` Schema
| Key        | Rule                                                                           |
|------------|--------------------------------------------------------------------------------|
| `name`     | Match the repo name (`coexistence-sim`). Avoid spaces.                         |
| `channels` | List **conda‑forge** first, then `defaults`.                                   |
| `dependencies` | Pin **major.minor** versions (`numpy=1.26.*`). Leave patch unconstrained unless a specific bugfix is required. |
| `- pip:`   | Group non‑conda packages here; version‑pin as in `requirements.txt`.           |
| Comments   | Explain *why* a package is included when not obvious.                          |

Example:
```yaml
name: coexistence-sim
channels:
  - conda-forge
  - defaults
dependencies:
  - python=3.11
  - numpy=1.26.*
  - scipy=1.12.*
  - httpx=0.27.*          # via conda-forge
  - pip
  - pip:
      - structlog~=24.1
      - tenacity~=8.3
```

### 6.3 Lock Files for Reproducibility
* Generate a deterministic lockfile with **conda‑lock**:  
  ```bash
  conda-lock -f environment.yml -p linux-64 -p win-64 -p osx-64
  ```
  Commit the resulting `conda-lock.yml`.  
* CI uses the lockfile:  
  ```bash
  conda-lock install --name coexistence-sim
  ```
* Do **not** edit the lockfile by hand.

### 6.4 License Compliance
1. Record SPDX identifiers for every dependency (`poetry export --with licenses`).  
2. Generate `THIRD‑PARTY‑NOTICES.md` during release.  
3. CI fails on GPLv3, AGPL, SSPL, or unknown licenses.

### 6.5 Supply‑Chain Security
* Run `pip-audit` on every push; block known CVEs over severity 7.  
* Verify release signatures with `pip install --require-hashes` in air‑gapped builds.  
* Mirror wheels in an internal index for repeatable deploys.

---

## 7. Imports & Module Organization

### 7.1 Import Ordering
1. Standard library  
2. Third‑party packages  
3. First‑party (this repo)  
Each group separated by one blank line. `isort` with the profile `black` enforces it.

```python
import json
from pathlib import Path

import httpx

from coexistence_simulator.utils.paths import DATA_DIR
```

### 7.2 Absolute vs Relative
* Prefer absolute imports to make file moves painless.  
* Use explicit relative imports (`from .subpkg import foo`) **only** for intra‑package helper modules.  
* Never chain relative levels (`from ...helpers import bar`).

### 7.3 Lazy Imports
* Delay heavyweight imports (`pandas`, `tensorflow`) inside functions that actually need them.  
* Wrap optional imports in try/except and document the extra feature flag.

### 7.4 Public API Exposure
Create a minimal surface in each package’s `__init__.py`:

```python
"""Top‑level package for coexistence‑simulator."""

from .core import Simulator, Scenario
from .version import __version__

__all__: list[str] = ["Simulator", "Scenario", "__version__"]
```

### 7.5 Cyclic Import Avoidance
* Place shared constants in a dedicated `constants.py`.  
* Move side‑effect code behind `if __name__ == "__main__":` guards.  
* When cycles sneak in, refactor rather than rely on `typing.TYPE_CHECKING`.

---

## 8. Testing Strategy

### 8.1 Test Types
| Layer            | Frameworks     | Purpose                                  |
|------------------|---------------|------------------------------------------|
| Unit             | `pytest`      | Pure logic in isolation, run in <50 ms.  |
| Property‑based   | `hypothesis`  | Explore edge cases automatically.        |
| Integration      | `pytest`      | Verify components together, may hit I/O. |
| End‑to‑end (E2E) | `pytest + any external harness` | Smoke‑test full CLI or service. |

### 8.2 Structure
```
repo/
├── src/
└── tests/
    ├── unit/
    ├── integration/
    └── e2e/
```

* Mirror package paths under `tests/unit` for readability.  
* Use fixtures, not `setUp`/`tearDown`.  
* Mark slow tests with `@pytest.mark.slow` and exclude by default (`-m "not slow"`).

### 8.3 Coverage & Quality Gates
* Target ≥ 80 % statement coverage; lines marked `# pragma: no cover` require reviewer sign‑off.  
* Mutation testing with `mutmut` for safety‑critical algorithms; score ≥ 80 %.  
* `flake8-docstrings` ensures every public symbol has documentation.

### 8.4 Mocking Guidelines
* Mock external boundaries (disk, network) only.  
* Prefer `pytest‑mock` (wraps `unittest.mock`) for succinct syntax.  
* Verify invariants, not implementation details.

### 8.5 Data Generation
* Use `faker` for fake personal data, not real names.  
* Keep static binary fixtures under `tests/fixtures/`, ≤ 100 kB each to avoid repository bloat.

---

## 9. Continuous Integration / Pre‑Commit

### 9.1 Pipeline Stages
| Stage      | Purpose                              |
|------------|--------------------------------------|
| Lint       | Run Ruff (`ruff check`), Black (`--check`), isort (`--check`). |
| Types      | `mypy --strict` or Pyright strict.   |
| Tests      | `pytest -n auto --durations=10`.     |
| Docs       | Build Sphinx, fail on warnings.      |
| Package    | Build wheel, run `twine check`.      |

### 9.2 Supported Runners
* GitHub Actions `ubuntu-latest`, `windows-latest`, and `macos-latest`.  
* Python versions: 3.11 (minimum) and 3.12 (latest stable).  
* Matrix builds enable catching platform quirks early.

### 9.3 Required Checks
* `lint`, `types`, `tests` must turn green for any non‑draft pull request.  
* Merge must happen through a pull request with at least one approving review.  
* Squash merge to keep history linear.

### 9.4 Commit Messages
Follow [Conventional Commits]:
```
feat(cli): add JSON export option
fix(sim): correct Doppler shift calculation
docs: clarify antenna model interface
```
Messages outside this syntax trigger a CI warning.

---

## 10. Performance Guidelines

### 10.1 Measure First
* Use `timeit`, `cProfile`, or `py‑instrument` to find hotspots.  
* Guard benchmarks under `bench/` and run with `pytest‑benchmark`.

### 10.2 Algorithm Before Micro‑Optimizing
* Moving from O(n²) to O(n log n) beats micro tricks every time.  
* Use set membership, heaps, and bisect where suitable.

### 10.3 CPU‑Bound Tasks
* Prefer NumPy or `numba` for large numeric loops.  
* Release the GIL with `concurrent.futures.ProcessPoolExecutor` if the workload is pickle‑friendly.  
* For *tiny* tight loops, consider Cython but only after profiling justifies the extra complexity.

### 10.4 I/O‑Bound Tasks
* Batch disk writes; avoid small random writes.  
* Reuse HTTP sessions (`httpx.AsyncClient`) to keep connections alive.  
* Prefer async over threads when large numbers of sockets are idle.

### 10.5 Memory Footprint
| Symptom              | Remedy                         |
|----------------------|--------------------------------|
| High RSS             | Chunk input in streams.        |
| Fragmentation        | Use `array.array` or NumPy.    |
| Leaks in loops       | Profile with `tracemalloc`.    |

### 10.6 Caching
* Employ `functools.lru_cache` for pure functions with small argument space.  
* In long‑running services, consider `cachetools.TTLCache` to bound growth.

### 10.7 Example Profiling Session
```shell
python -m cProfile -o stats.prof -m coexistence_simulator.cli run-scenario demo.json
snakeviz stats.prof
```

### 10.8 CI Performance Budget
* Benchmarks must not regress > 5 % relative to the `main` branch median.  
* `pytest‑benchmark` compares `–benchmark‑compare` and fails on exceedance.

---
## 11. Concurrency Rules

### 11.1 Choose One Model Per Subsystem
| Model      | Best For                       | Caveats                                    |
|------------|--------------------------------|--------------------------------------------|
| Threads    | Blocking I/O with small count  | GIL limits CPU parallelism; watch race conditions. |
| `multiprocessing` | CPU parallelism          | IPC overhead; objects must be pickleable. |
| `asyncio`  | Massive I/O concurrency        | Requires non‑blocking libraries; one loop per thread. |
| `trio`     | Structured concurrency         | Different API; wrap third‑party asyncio via `anyio`. |

### 11.2 Thread‑Safety Checklist
1. Immutable data structures first (`tuple`, `frozenset`).  
2. If shared mutable state is unavoidable, guard with `threading.Lock` or `RLock`.  
3. Log with thread‑safe handlers (`queue.QueueHandler`).  
4. Avoid global caches in libraries—let the caller choose concurrency strategy.

### 11.3 Async Coding Standards
* Each public async API must include “… async …” in docstring **Synopsis**.  
* Never call blocking code inside `async def`; offload with `run_in_executor`.  
* Shield cancellation for critical sections (`asyncio.shield`).  
* Use structured concurrency (`async with trio.open_nursery()`) to avoid orphan tasks.

### 11.4 Process Pools
* Default to `concurrent.futures.ProcessPoolExecutor(max_workers=os.cpu_count())`.  
* For large arrays, share memory via `multiprocessing.shared_memory` or **PyArrow Plasma**.  
* Gracefully shut down pools in `atexit` handlers to avoid zombies.

### 11.5 Event Loop Policy
* Libraries must **not** call `asyncio.run()` directly—offer `async def main()` instead.  
* CLI wrappers call `asyncio.run()` under `if __name__ == "__main__":`.

---

## 12. Security Practices

### 12.1 Secrets Management
| Context           | Rule                                          |
|-------------------|-----------------------------------------------|
| Local dev         | `.env` loaded via `python‑dotenv`, *not committed*. |
| CI / prod         | Retrieve from secure store (GitHub Secrets, AWS Secrets Manager, HashiCorp Vault). |
| Testing           | Inject via fixtures; never real credentials.  |

Use `dotenv-linter` pre‑commit hook to block accidental commits of keys.

### 12.2 Input Validation
* Validate external input at boundaries with **Pydantic** or custom validators.  
* Reject dangerous characters early (e.g., path traversal `../`).  
* When deserializing YAML, call `yaml.safe_load`.

### 12.3 Cryptography
* Use **libsodium / pynacl** or **cryptography**; never roll your own.  
* Default algorithms:  
  * Hashing: `blake2b` or `sha256`.  
  * Symmetric: `AES‑256‑GCM`.  
  * Asymmetric: `Ed25519` for signatures.  
* Rotate keys annually; store key metadata (`kid`, algorithm, creation date).

### 12.4 Transport Security
* Enforce TLS 1.2+; verify certificates (`httpx` does by default).  
* For self‑signed certs in staging, pin SHA‑256 fingerprints instead of disabling verification.

### 12.5 Static & Dependency Scanning
* **Ruff** rules: `RUF100` series for insecure usages (`eval`, `exec`).  
* `bandit -r src/` in CI; severity ≥ medium blocks.  
* `pip-audit` and `conda-tree audit` for CVEs; produce SBOM (`cyclonedx‑python‐lib`).

### 12.6 Sandboxing User Code
If executing user‑supplied Python (rare):
* Use **PyOddly** or **Subprocess** with seccomp filters—not `exec` in‑process.  
* Containerize with read‑only filesystem; drop privileges to non‑root UID.

---

## 13. Packaging & Distribution

### 13.1 Artifacts
| Artifact | Tool | Notes |
|----------|------|-------|
| Wheel    | `python -m build` | Upload to **PyPI** and internal index. |
| Conda    | `conda-build` | Recipe under `conda-recipe/`. |
| Source   | sdist tarball   | Optional; ensure `pyproject.toml` includes `sdist` tag. |

### 13.2 Versioning Policy
* **SemVer** (`MAJOR.MINOR.PATCH`) for libraries.  
* **CalVer** (`YYYY.M`) for CLI applications with monthly cadence.  
* Breaking changes require a deprecation period ≥ one minor release.

### 13.3 Entry Points
Declare CLIs in `pyproject.toml`:
```toml
[project.scripts]
coex-sim = "coexistence_simulator.cli:main"
```
* CLI must parse `--version` and return semver.  
* Provide `--help` generated via `typer` or `argparse`, covered by tests.

### 13.4 Reproducible Builds
* Run `python -m build --no-isolation`; pin exact build‑deps in `pyproject.toml`.  
* Enable **Source Date Epoch**:
  ```bash
  export SOURCE_DATE_EPOCH=$(git log -1 --pretty=%ct)
  ```

### 13.5 Publishing Workflow
1. Tag `vX.Y.Z` in Git; GitHub Actions build wheels for all platforms.  
2. Sign artifacts with **Sigstore** (`sigstore-python`); attach `.sig` to release.  
3. `twine upload --skip-existing --sign` to PyPI.  
4. Bump `__version__` and deploy updated docs.

---

## 14. Internationalization & Localization

### 14.1 Unicode Policy
* Source files remain **ASCII‑only** per Section 1.6; user‑facing strings may include Unicode.  
* Store text as `str` (UTF‑8 internally); convert at I/O boundaries.

### 14.2 Pluralization & Formatting
* Use **Babel** for locale‑aware formatting:
  ```python
  from babel.numbers import format_decimal
  format_decimal(1234.5, locale="fr_FR")  # '1 234,5'
  ```
* Keep translation keys in `.po` files; extract with `pybabel extract`.

### 14.3 Date & Time
* Internal times are `datetime` with `zoneinfo.ZoneInfo("UTC")`.  
* Format for display with user locale, e.g., `babel.dates.format_datetime`.

### 14.4 Right‑to‑Left (RTL) Support
* Avoid string concatenation for layout; rely on UI frameworks that auto‑mirror.  
* Store bi‑di markers only when essential (`\u200F`, `\u200E`).

### 14.5 Testing Strategy
* Include smoke tests running with `LANG=ja_JP.UTF-8` and `LANG=ar_SA.UTF-8`.  
* Validate that no `UnicodeEncodeError` occurs under `PYTHONIOENCODING=ascii`.

---

## 15. Data Handling & Persistence

### 15.1 Filesystem Access
* Use **Pathlib** (`Path("data") / "raw" / fname`).  
* Guard against path traversal:
  ```python
  dest = safe_base / unsafe_name
  dest.resolve(strict=False).relative_to(safe_base)
  ```

### 15.2 Time Zones & Timestamps
| Rule                                     | Example                                    |
|------------------------------------------|--------------------------------------------|
| Always store UTC in databases            | `created_at TIMESTAMP WITH TIME ZONE`      |
| Include offset in serialized JSON fields | `"2025-07-18T03:04:05.678Z"`               |
| Convert to local at UI boundary          | Via `zoneinfo.ZoneInfo(user_tz)`           |

### 15.3 Serialization Formats
| Use‑case                 | Recommended Format | Library                       |
|--------------------------|--------------------|-------------------------------|
| Human‑configurable text  | TOML               | `tomli`, `tomlkit`            |
| Logging / metrics        | JSON Lines         | `orjson`, newline‑delimited   |
| Large tabular numeric    | Parquet           | `pyarrow.parquet`             |
| Inter‑service binary RPC | MessagePack       | `msgpack‑python`              |

Avoid **Pickle** for untrusted data; prefer JSON/MsgPack.

### 15.4 Databases
* SQL first (**PostgreSQL**); schema versioned with **Alembic**.  
* Use connection pooling (`asyncpg.create_pool`).  
* ORM allowed (`SQLAlchemy 2.x`) but keep business rules out of models.

### 15.5 Transactions
| Pattern                 | Rule                              |
|-------------------------|-----------------------------------|
| Multiple writes         | Wrap in `WITH` transaction block. |
| Long‑running operations | Use optimistic concurrency IDs.   |
| Retry serialization fail| `psycopg.errors.SerializationFailure`; exponential back‑off. |

### 15.6 Data Privacy
* Mask PII at rest (`hash_email(email)`) when feasible.  
* Encrypt disks or cloud buckets with AES‑256.  
* Build GDPR/CCPA delete pipeline; verify via integration tests.

---

## 16. Configuration Management

### 16.1 Source of Configuration Truth
| Priority | Location               | Example               |
|----------|------------------------|-----------------------|
| 1        | Command‑line flags     | `--port 8080`         |
| 2        | Environment variables  | `COEX_PORT=8080`      |
| 3        | Config file (`*.yaml`) | `config.yaml`         |
| 4        | Hard‑coded defaults    | `DEFAULT_PORT = 8000` |

Configuration resolution follows this order; higher tiers override lower.

### 16.2 Schema Validation
* Use **Pydantic v2** `BaseSettings` subclass:
  ```python
  class Settings(BaseSettings):
      port: int = Field(8000, ge=1, le=65535)
      db_url: SecretStr
      class Config:
          env_prefix = "COEX_"
          env_file = ".env"
  settings = Settings()  # auto‑loads env vars & .env
  ```
* Fail fast on invalid config; exit code 78 (configuration error).

### 16.3 Hot Reloading
| Context      | Policy                               |
|--------------|--------------------------------------|
| CLI tools    | No hot reload—re‑run with new flags. |
| Long‑running services | SIGHUP triggers reload of config file & environment, but **not** CLI flags. Implement watch loop with `watchdog`. |

### 16.4 Secrets in Config
* Reference secrets via env vars **only**; never embed in config files.  
* Accept Vault placeholders (`"vault://path#key"`) and resolve at startup.  
* CI linter rejects secrets using regex heuristics (AWS keys, Slack tokens).

### 16.5 Hierarchical Config Example – `config.toml`
```toml
[http]
port = 8080
read_timeout_secs = 10
write_timeout_secs = 10

[database]
url = "postgresql+asyncpg://coex@localhost:5432/db"

[logging]
level = "INFO"
json = true
```

### 16.6 Testing Configuration
* Parametrize unit tests with representative configs via `pytest‑cases`.  
* Ensure missing or corrupt config raises `SystemExit` with code 78.

---

## 17. Compatibility & Deprecation

### 17.1 Supported Python Versions
| Status         | Minor Versions | Action                                               |
|----------------|----------------|------------------------------------------------------|
| **Current**    | 3.12, 3.11     | CI must pass; new syntax features allowed.           |
| **Deprecated** | 3.10           | Accept patches only; no new features relying on 3.10 |
| **EOL**        | ≤ 3.9          | Breaks may be introduced without notice.            |

Drop a version when the Python core team declares End‑of‑Life **or**
when the dependency graph makes backports unreasonably costly.

### 17.2 Deprecation Process
1. Mark function/class with `@deprecated("Will be removed in v3.0")`.  
2. Emit `DeprecationWarning`; tests run with `-Werror::DeprecationWarning` to keep track.  
3. Document replacement in docstring and changelog.  
4. Remove after one **minor** release cycle or six months, whichever is longer.

### 17.3 Semantic Versioning Enforcement
* Breaking API = raise major version.  
* Adding param with default = minor bump.  
* Bug fix / docs only = patch.

CI compares current `__version__` to public API diff (`python‑semantic‑release changelog --noop`).

### 17.4 Backwards‑Compatibility Shims
* Place in `coexistence_simulator.compat`.  
* Must include `TODO(remove)` comment with version.  
* No more than one shim layer deep.

---

## 18. Code Review Etiquette

### 18.1 Pull Request Checklist
- [ ] All CI checks green (lint, type, tests, docs).  
- [ ] Added/updated unit tests & docs.  
- [ ] Coverage ≥ 80 % (or justified).  
- [ ] No secrets or personal data in diff.  
- [ ] Public API changes annotated in `CHANGELOG.md`.  

### 18.2 Reviewer Guidelines
| Aspect            | Look For                                     |
|-------------------|----------------------------------------------|
| Correctness       | Logical errors, race conditions.             |
| Readability       | Clear naming, small functions, comments.     |
| Scope             | PR does one thing; no drive‑by refactor unless agreed. |
| Tests             | Adequate coverage, meaningful assertions.    |
| Perf & security   | Obvious inefficiencies, insecure patterns.   |

Avoid “nit” wars: batch minor issues in a single comment or suggest `pre‑commit autoupdate`.

### 18.3 Turnaround Time
* **Author** responds to review feedback within **2 business days**.  
* **Reviewer** should provide first pass within **1 business day** of assignment.

### 18.4 Approvals
* Minimum **one** reviewer for non‑critical code, **two** for security‑sensitive paths.  
* Do not self‑approve unless sole maintainer of the module.

### 18.5 Merging Strategy
| Branch    | Strategy          | Rationale                                |
|-----------|-------------------|------------------------------------------|
| `main`    | Squash & merge    | Clean linear history, each PR one commit |
| Release X | Cherry‑pick fixes | Avoid unwanted commits in patch release  |

---

## 19. Ethics & Inclusivity

### 19.1 Inclusive Language
* Prefer `allowlist/denylist`, `primary/replica`, `parent/child`.  
* Avoid gendered pronouns in docs; use “they” or second‑person.

### 19.2 Accessibility
* Code examples should compile/run with default fonts and color schemes.  
* Doc diagrams must include alt text; colors must pass WCAG AA contrast.

### 19.3 Data Sets
* Public domain or permissively licensed.   
* Annotate synthetic data generation process.

### 19.4 AI Ethics
* Disclose training data sources for any ML component.  
* Document known biases and mitigation strategy.

---

## 20. Legal Headers & Compliance

### 20.1 Third‑Party Notices
* Maintain `THIRD‑PARTY‑NOTICES.md` enumerating licenses for bundled deps.  
* Regenerate with `reuse spdx‑sbom` on release tag.

### 20.2 Export Compliance
* Crypto exports: classify under ECCN 5D002; publish open‑source notice to qualify for license exception TSU.  
* Exclude embargoed countries from PyPI/Conda downloads using repository CDN rules.

### 20.3 Trademark Usage
* Use ® and ™ symbols only in marketing docs, not in code.  
* Respect upstream project trademark guidelines (e.g., “PostgreSQL”, not “PostgresSQL”).

### 20.4 Contributor IP Assignment & Patents
* **Contributor License Agreement (CLA)** — Every external contributor must sign the project CLA *before* a PR is merged.  The CLA:
  1. **Assigns** to Stephen Itschner all copyrights and patent rights in the contribution.  
  2. Grants the contributor a perpetual, worldwide, royalty‑free license to use their own code.  
  3. Includes a defensive termination clause (if you sue, you lose the license).  

* PRs without a green “CLA Signed” check cannot be merged.

* Code that references third‑party patents or otherwise‑encumbered algorithms **must** be flagged with `# PATENT‑NOTICE:` and receive legal review before merge.

---

