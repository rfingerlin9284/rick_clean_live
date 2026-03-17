# 🏗️ Build RICK From Scratch — No Coding Required
### Using VSCode + Antigravity Agent | Only needs what's on GitHub

> **Who this is for:** You have no local files. You can't code. You have VSCode with the Antigravity agent installed. You want to clone the latest version of RICK from GitHub and have the Antigravity agent set everything up for you.

---

## ✅ Before You Start — Install These (One-Time)

You only need to do this once. Click each link and follow the installer:

| Tool | Download Link | Why You Need It |
|------|--------------|-----------------|
| **Git** | https://git-scm.com/downloads | Downloads the code from GitHub |
| **Python 3.11+** | https://www.python.org/downloads/ | Runs the trading system |
| **VSCode** | https://code.visualstudio.com/ | Your coding environment |

> ⚠️ **Windows users installing Python:** On the first installer screen, tick **"Add Python to PATH"** before clicking Install.

---

## 📥 Step 1 — Download the Latest Code from GitHub

You have two options. Pick whichever feels easier:

### Option A: Using Git (Recommended — gets all branches)

1. Open a terminal:
   - **Windows:** Press `Win + R`, type `cmd`, press Enter
   - **Mac:** Press `Cmd + Space`, type `Terminal`, press Enter
2. Copy and paste this command, then press Enter:
   ```
   git clone https://github.com/rfingerlin9284/rick_clean_live.git
   ```
3. A new folder called `rick_clean_live` will appear wherever your terminal is open (usually your home folder).

### Option B: Download ZIP (No Git needed — gets only the current branch)

1. Go to: https://github.com/rfingerlin9284/rick_clean_live
2. Click the green **`<> Code`** button
3. Click **Download ZIP**
4. Unzip the downloaded file

---

## 📂 Step 2 — Open the Folder in VSCode

1. Open **VSCode**
2. Click **File → Open Folder**
3. Navigate to and select the `rick_clean_live` folder you just downloaded
4. Click **Open**

You should now see all the project files in the left sidebar.

---

## 🤖 Step 3 — Open the Antigravity Agent in VSCode

1. In VSCode, open the **Antigravity Agent** panel
   - It is usually a sidebar icon or accessible from the Command Palette (`Ctrl+Shift+P` → type `Antigravity`)
2. Make sure it is connected and ready to accept prompts

---

## 🚀 Step 4 — Copy & Paste These Prompts Into the Antigravity Agent

Run these **one at a time**, in order. Wait for each one to finish before moving to the next.

---

### Prompt 1 — Install All Dependencies

> Copy this entire block and paste it into Antigravity:

```
Open a terminal in this project folder and run:

pip install -r requirements.txt

Wait for it to complete. If there are any errors, read them carefully and try to fix them by installing missing packages. When done, confirm "Dependencies installed successfully."
```

---

### Prompt 2 — Create Your Environment Configuration File

> Copy this entire block and paste it into Antigravity:

```
In the project root folder, create a new file called `.env` by copying the example file `.env.example`.

On Windows the terminal command is:
  copy .env.example .env

On Mac/Linux the terminal command is:
  cp .env.example .env

After creating it, open `.env` in the editor and show me its contents so I can fill in my API keys.
```

> **After Antigravity creates the file**, you will need to fill in your API keys:
> - **OANDA_API_TOKEN** and **OANDA_ACCOUNT_ID** — Get these from https://www.oanda.com (free practice account)
> - **COINBASE_API_KEY** and **COINBASE_API_SECRET** — Get these from https://www.coinbase.com/settings/api (optional)
> - Leave `OANDA_ENVIRONMENT=practice` and `PAPER_MODE=true` for safe testing

---

### Prompt 3 — Verify the System Is Ready

> Copy this entire block and paste it into Antigravity:

```
Open a terminal in this project folder and run the system status check:

make status

Read the output and tell me:
1. What is the current trading mode?
2. Are any engines currently running?
3. Are there any errors I need to fix?
```

---

### Prompt 4 — Start Paper Trading (Safe, No Real Money)

> Copy this entire block and paste it into Antigravity:

```
Open a terminal in this project folder and start the paper trading engine in the background:

make paper-48h

This runs for 48 hours using a practice (demo) account — no real money is at risk.

After starting it, run:
  make status

Then run:
  make logs

Tell me what you see and confirm the system is running correctly.
```

---

### Prompt 5 — Open the Dashboard (Optional)

> Copy this entire block and paste it into Antigravity:

```
Open a terminal in this project folder and start the web dashboard:

make dashboard

After it starts, open a web browser and go to:
  http://127.0.0.1:8501

Take a screenshot or describe what you see on the dashboard.
```

---

### Prompt 6 — Monitor Your Trades

> Copy this entire block and paste it into Antigravity:

```
Open a terminal in this project folder and show me the live narration feed (plain English trade activity):

make narration

Let it run for 2 minutes and show me what trades or activity you see.
```

---

## 🛑 How to Stop Everything

Paste this into Antigravity at any time to safely stop all trading:

```
Open a terminal in this project folder and stop all running engines:

make stop

Then run:
  make status

Confirm everything has stopped.
```

---

## 🔑 Important Settings Reference

| Setting | File | Default | What it means |
|---------|------|---------|---------------|
| `PAPER_MODE` | `.env` | `true` | **True = no real money**. Keep this `true` until you are confident |
| `OANDA_ENVIRONMENT` | `.env` | `practice` | `practice` = demo account. `live` = real money |
| `MAX_TOTAL_EXPOSURE_USD` | `.env` | `1000.0` | Maximum USD at risk across all trades |
| `MIN_CONFIDENCE` | `.env` | `0.65` | Minimum signal confidence before placing a trade |

> ⚠️ **Never change `PAPER_MODE` to `false` or `OANDA_ENVIRONMENT` to `live` until you have tested for at least 48 hours and are comfortable with the system.**

---

## 🆘 Troubleshooting — Paste These Into Antigravity If Something Goes Wrong

**"pip install failed / Python not found"**
```
Check if Python is installed by running:
  python --version
  python3 --version

If neither works, Python is not installed or not on the PATH. Help me fix this.
```

**"make: command not found" (Windows)**
```
On Windows, 'make' is not installed by default. Install it by running:
  winget install GnuWin32.Make

Or alternatively, show me how to run the equivalent Python commands directly without using make.
```

**"Module not found" errors when starting the engine**
```
Open a terminal and run:
  pip install -r requirements.txt

Then try starting the engine again with:
  make paper
```

**"OANDA API connection failed"**
```
Open the .env file and check:
1. OANDA_API_TOKEN is set to a real token (not "your_oanda_api_token_here")
2. OANDA_ACCOUNT_ID is set to a real account ID
3. OANDA_ENVIRONMENT is set to "practice"

Guide me to get a free OANDA practice account and API token at https://www.oanda.com
```

---

## 📋 Quick Command Cheat Sheet

Paste any of these into Antigravity at any time:

| What you want | Paste into Antigravity |
|---------------|----------------------|
| Check if system is running | `Run: make status` |
| Start paper trading | `Run: make paper-48h` |
| Open dashboard | `Run: make dashboard` |
| Watch live trade feed | `Run: make narration` |
| See recent logs | `Run: make logs` |
| Stop everything | `Run: make stop` |
| Run tests | `Run: make test` |

---

## 📚 Further Reading (Already in This Repo)

Once the system is running, you can learn more by asking Antigravity to read these files for you:

- `QUICK_START_GUIDE.md` — Detailed guide to the trading engine
- `PAPER_MODE_VALIDATION.md` — How to validate your paper trading results
- `GITHUB_UPDATE_GUIDE.md` — How to update the system when a new version is released
- `TROUBLESHOOTING_GUIDE.md` — More detailed troubleshooting help

---

**Status:** ✅ Ready to Use | **Skill Required:** None — just copy and paste  
**Charter PIN:** 841921 | **Default Mode:** Paper Trading (safe)
