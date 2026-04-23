# 📦 BB Downloader

> Automatically download **all** course files from [Blackboard Learn](https://www.blackboard.com/) with a single command.

---

## ✨ Features

| Feature | Description |
|---------|-------------|
| 🔐 **Browser Login** | Opens a browser for SSO / CAS / campus login — no password stored |
| 🍪 **Cookie Cache** | Saves session cookies locally; skip re-login on next run |
| 📚 **Course Selection** | Lists enrolled courses, supports keyword filtering |
| 📂 **Directory Mirroring** | Preserves Blackboard's folder structure on disk |
| ⏭ **Incremental Sync** | Skips already-downloaded files (size-based check) |
| 📊 **Rich Progress** | Real-time progress bars with speed & ETA |
| 🔄 **Auto Retry** | Failed downloads retry up to 3 times with exponential backoff |
| 📄 **`.env` support** | Loads `BB_BASE_URL` (and optional flags) from a project `.env` via `python-dotenv` |
| 🔒 **Campus TLS** | Relaxed TLS defaults for `requests` when OpenSSL 3 handshakes fail (browser still works); opt out with `BB_TLS_STRICT` |

## 📋 Prerequisites

- **Python** ≥ 3.10
- **Chrome** or **Edge** browser
- A valid campus account with Blackboard access

## 🚀 Quick Start

### 1. Clone & install

```bash
git clone https://github.com/ACM1966/BB-Downloader.git
cd BB-Downloader
pip install -r requirements.txt
```

### 2. Configure

Copy the example environment file and set your Blackboard URL:

```bash
cp .env.example .env
```

Edit `.env`:

```ini
BB_BASE_URL=https://bb.your-university.edu
# Optional: use system-default TLS only (disable campus compatibility adapter)
# BB_TLS_STRICT=1
```

The app **loads `.env` automatically** on startup (you do not need to export variables manually unless you prefer that).

> **Tip:** You can still set `BB_BASE_URL` (and `BB_TLS_STRICT`) in the shell instead of `.env`.  
> If `BB_BASE_URL` is missing, the placeholder URL is used and connections will fail.

### 3. Run

```bash
python main.py
```

**First login:** a browser window opens — **log in with your campus account**. The program detects login automatically, validates the Blackboard REST API, then continues (course list / download).

**Later runs:** if `cookies.json` is still valid, the browser **does not** open. To force a browser login again, run `python main.py --relogin` or delete `cookies.json`.

### 4. Output

Files are saved to `./downloads/` by default:

```
downloads/
├── Course A/
│   ├── Week 1/
│   │   ├── lecture1.pdf
│   │   └── homework1.docx
│   └── Week 2/
│       └── lecture2.pptx
└── Course B/
    └── ...
```

## ⚙️ CLI Options

```
usage: main.py [-h] [-o OUTPUT_DIR] [-c [COURSE ...]] [--relogin] [--all]
```

| Flag | Description | Example |
|------|-------------|---------|
| `-o, --output-dir` | Custom download directory | `python main.py -o D:\courses` |
| `-c, --course` | Filter courses by keyword | `python main.py -c "Math" "Physics"` |
| `--all` | Download all courses (skip prompt) | `python main.py --all` |
| `--relogin` | Force re-login (ignore cached cookies) | `python main.py --relogin` |

#### Examples

```bash
# Download everything
python main.py --all

# Save to a specific folder
python main.py -o D:\BlackboardFiles

# Only courses matching "CSC"
python main.py -c CSC

# Force re-login + download all
python main.py --relogin --all
```

## 🔧 Environment variables

| Variable | Required | Description |
|----------|----------|-------------|
| `BB_BASE_URL` | Yes* | Blackboard site root, e.g. `https://bb.your-university.edu` (no trailing path). Set in `.env` or the shell. |
| `BB_TLS_STRICT` | No | If `1` / `true` / `yes`, disables the TLS compatibility adapter and uses urllib3/OpenSSL defaults. |

\*Required in practice: without it, the default placeholder URL is used and requests will fail.

Values from a project **`.env`** are loaded automatically when you run `python main.py`.

## 🏗 Architecture

```
main.py          CLI entry point — argument parsing, course selection, orchestration
auth.py          Browser login (Selenium) → cookies → requests session + TLS compat + validation
api.py           Blackboard Learn REST API client (paginated, with error handling)
downloader.py    Recursive content traversal + streaming file download with progress
config.py        Loads `.env`, URLs, timeouts, retry policy
```

**Flow:**

```
Browser login (or valid cookies.json) → requests session + TLS compat → REST API /users/me
    → /users/{id}/courses → /courses/{id}/contents (recursive)
        → /attachments/{id}/download (streamed)
```

## 📝 Notes

- First run requires manual browser login; subsequent runs reuse cached cookies (`cookies.json`, git-ignored).
- Cookies expire based on server policy — the tool validates the API and will ask you to log in again when cookies no longer work.
- Some campuses use TLS chains or cipher settings that make **Python/`requests` fail with `SSLV3_ALERT_HANDSHAKE_FAILURE`** even though Chrome works. This project mounts a **compatible TLS adapter** (still verifies certificates) by default. Set **`BB_TLS_STRICT=1`** in `.env` or the environment if you need the default urllib3/OpenSSL behavior.
- If login in the browser succeeds but the CLI reports **API / authentication failure**, check the printed diagnostics. **HTTP 403** on `/learn/api/public/v1` often means the institution has restricted the **Public REST API** for your role.
- Courses with instructor-set access restrictions may not be downloadable.
- Watch your disk space when downloading many courses.

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue first to discuss proposed changes.

## ⚖️ Disclaimer

This tool is intended for **personal, educational use only** — to help students back up their own course materials. Please respect your institution's terms of service and intellectual property policies.

## 📄 License

[MIT](LICENSE)
