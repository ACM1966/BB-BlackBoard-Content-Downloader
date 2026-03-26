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
```

> **Tip:** You can also set the `BB_BASE_URL` environment variable directly instead of using a `.env` file.  
> If left unconfigured, the tool will use the placeholder URL and fail to connect.

### 3. Run

```bash
python main.py
```

A browser window will open — **log in with your campus account**. The program detects login automatically and starts downloading.

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

## 🏗 Architecture

```
main.py          CLI entry point — argument parsing, course selection, orchestration
auth.py          Browser-based login via Selenium → cookie extraction → session reuse
api.py           Blackboard Learn REST API client (paginated, with error handling)
downloader.py    Recursive content traversal + streaming file download with progress
config.py        Central configuration (URLs, timeouts, retry policy)
```

**Flow:**

```
Browser Login → Extract Cookies → REST API /users/me
    → /users/{id}/courses → /courses/{id}/contents (recursive)
        → /attachments/{id}/download (streamed)
```

## 📝 Notes

- First run requires manual browser login; subsequent runs reuse cached cookies.
- Cookies expire based on server policy — the tool auto-detects expiry and prompts re-login.
- Courses with instructor-set access restrictions may not be downloadable.
- Watch your disk space when downloading many courses.

## 🤝 Contributing

Pull requests and issues are welcome! Please open an issue first to discuss proposed changes.

## ⚖️ Disclaimer

This tool is intended for **personal, educational use only** — to help students back up their own course materials. Please respect your institution's terms of service and intellectual property policies.

## 📄 License

[MIT](LICENSE)
