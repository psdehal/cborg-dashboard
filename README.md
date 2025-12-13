# CBORG Dashboard

A terminal-based dashboard for monitoring LBNL CBORG service usage and models.

## Features

- 📊 Track 181+ AI models from OpenAI, Anthropic, Google, xAI, and LBL-hosted services
- 🆕 Automatically detect and highlight new models since your last check
- 💰 Monitor API spending (when available via API)
- 🔑 Support multiple API keys with separate tracking for each
- 💾 Local JSON-based storage for historical data
- 🎨 Beautiful terminal UI with color-coded output

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

The dashboard displays:
1. **Connection Status** - Verifies API connectivity
2. **Model Summary** - Total models, new models, and last check time
3. **New Models** - Highlighted table of newly discovered models (yellow)
4. **All Models** - Complete list organized alphabetically
   - Green: LBL-hosted models (lbl/*)
   - Cyan: Commercial models (OpenAI, Anthropic, Google, etc.)
5. **Spend Information** - Current spend and budget (when API supports it)

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

Team mode displays:
- Individual spending for each team member
- Team totals (spend, budget, remaining)
- Color-coded usage warnings (red >90%, yellow >75%, green <75%)

**Security Notes:**
- `team_keys.json` is gitignored (never committed)
- Use `chmod 600 team_keys.json` to restrict access
- Keep this file on encrypted disk (FileVault on macOS)
- Never share via email/Slack

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
