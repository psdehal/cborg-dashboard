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
