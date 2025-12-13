# CBORG Dashboard

A terminal-based dashboard for monitoring LBNL CBORG service usage and models.

## Features

### Core Functionality
- 📊 **Model Tracking** - Monitor 181+ AI models from OpenAI, Anthropic, Google, xAI, and LBL-hosted services
- 🆕 **New Model Detection** - Automatically detect and highlight new models since your last check
- 🎯 **Latest Frontier Models** - Quick view of top models from OpenAI, Anthropic, and Google
- 💰 **Spend Tracking** - Real-time budget monitoring with color-coded warnings
- 📈 **Spend History** - Automatic time-series tracking for trend analysis
- 👥 **Team Mode** - Multi-user dashboard for PIs managing team spending
- 🔑 **Multi-Key Support** - Track multiple API keys with separate data storage
- 💾 **Local Storage** - JSON-based storage indexed by API key hash
- 🎨 **Rich Terminal UI** - Beautiful color-coded output with tables and panels

### Team Management
- 👀 **Activity Monitoring** - Track last usage, key age, and expiration dates
- ⚠️ **Status Warnings** - Detect blocked keys, budget cooldowns, and inactive users
- 📊 **Team Analytics** - Aggregate spending, usage percentages, and activity trends
- 🔐 **Secure Configuration** - Gitignored team keys with 600 file permissions

## Quick Start

```bash
# 1. Create virtual environment
python3 -m venv venv
source venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your CBORG API key
export CBORG_API_KEY=your-key-here

# 4. Run the dashboard
python dashboard.py

# Or use the convenience script
./run.sh
```

## What You'll See

### Single-User Mode
1. **Connection Status** - Verifies API connectivity
2. **Model Summary** - Total models, new models, and last check time
3. **New Models** - Highlighted table of newly discovered models (yellow)
4. **All Models** - Complete list organized alphabetically
   - Green: LBL-hosted models (lbl/*)
   - Cyan: Commercial models (OpenAI, Anthropic, Google, etc.)
5. **Latest Frontier Models** - Top models from OpenAI, Anthropic, Google
6. **Spending Information** - Current spend, budget, remaining, usage %

### Team Mode
1. **Team Spending Overview** - Individual spending for each member
   - Sorted: PI first, then by spend (highest first)
   - Color-coded usage warnings
2. **Key Activity & Status** - Track team member activity
   - Sorted by last activity (most recent first)
   - Shows key age, last usage, expiration, status
3. **Team Totals** - Aggregate spending and budget across all members
4. **Latest Frontier Models** - Same as single-user mode

## Multiple API Keys

The dashboard automatically tracks data separately for each API key:

```bash
# Use different keys for different projects
export CBORG_API_KEY=key-for-project-1
python dashboard.py

export CBORG_API_KEY=key-for-project-2
python dashboard.py
```

Data is stored in `.cborg_data/` indexed by a hash of your API key.

## Team Mode

For PIs managing team spending, use `team_keys.json` to monitor multiple users at once:

```bash
# 1. Copy the template
cp team_keys.json.template team_keys.json

# 2. Edit team_keys.json with your team's information
nano team_keys.json

# 3. Set secure permissions (owner read/write only)
chmod 600 team_keys.json

# 4. Run dashboard - it will auto-detect team mode
python dashboard.py
```

Example `team_keys.json`:
```json
{
  "keys": [
    {
      "name": "Alice Smith",
      "email": "alice@lbl.gov",
      "api_key": "sk-...",
      "role": "PI"
    },
    {
      "name": "Bob Johnson",
      "email": "bob@lbl.gov",
      "api_key": "sk-...",
      "role": "Postdoc"
    }
  ]
}
```

**Team mode displays:**
- **Team Spending Overview**
  - Individual spending for each member (PI first, then sorted by spend)
  - Current spend, budget, remaining, usage percentage
  - Color-coded warnings: 🟢 green <75%, 🟡 yellow 75-90%, 🔴 red >90%
- **Key Activity & Status**
  - Last activity timestamp (sorted most recent first)
  - Key age (days since creation)
  - Expiration dates
  - Status warnings (Active, Cooldown, BLOCKED)
- **Team Totals**
  - Aggregate spending across all members
  - Total budget and remaining funds
  - Overall team usage percentage
- **Latest Frontier Models** (same as single-user mode)

**Use Cases:**
- Identify top spenders in your team
- Detect inactive team members (no activity in >7 days)
- Monitor for budget issues (blocked keys, cooldowns)
- Track team-wide spending trends

**Security Notes:**
- `team_keys.json` is gitignored (never committed)
- Use `chmod 600 team_keys.json` to restrict access
- Keep this file on encrypted disk (FileVault on macOS)
- Never share via email/Slack

## Data Storage & History

The dashboard automatically stores data in `.cborg_data/` indexed by API key hash:

```
.cborg_data/
├── c33edd494d929aa2.json  # Your key's data
├── 9ef74bb459ec8365.json  # Team member 1
└── 391ec8ce45ba2790.json  # Team member 2
```

**Each file contains:**
- API key preview (first 8 + last 4 chars)
- Known models list
- **Spend history** - Timestamped snapshots of spending
  - Only records when spend changes (no duplicates)
  - Stores up to 365 records (~1 year of daily checks)
  - Tracks: spend, budget, remaining, timestamp, key alias

**Spend history format:**
```json
{
  "spend": {
    "last_check": "2025-12-12T21:31:32",
    "history": [
      {
        "timestamp": "2025-12-12T21:31:32",
        "current_spend": 1992.57,
        "budget_limit": 4000.0,
        "remaining": 2007.43,
        "key_alias": "user@lbl.gov"
      }
    ]
  }
}
```

**Future Capabilities:**
With historical data accumulating, you can build:
- Spend velocity graphs: "Spending $15/day average"
- Budget projections: "Budget exhausted in ~45 days"
- Usage spike detection: "Spending jumped 300% yesterday"
- Team trend analysis: Who's ramping up vs slowing down
- Export to CSV/JSON for reporting

## CBORG Service

- **Web Interface**: https://cborg.lbl.gov
- **API Management**: https://api.cborg.lbl.gov/key/manage
- **Documentation**: https://cborg.lbl.gov/api_examples/

## Troubleshooting

**Error: CBORG_API_KEY not set**
```bash
export CBORG_API_KEY=your-actual-key
```

**Module not found errors**
```bash
source venv/bin/activate
pip install -r requirements.txt
```

**Virtual environment issues on macOS**
- Always use `python3 -m venv venv` to create the environment
- Don't use `--break-system-packages` flag
