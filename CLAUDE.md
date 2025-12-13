# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a terminal-based dashboard for monitoring the LBNL CBORG service. CBORG is a multi-model AI portal that provides access to various LLM services (OpenAI, Anthropic Claude, Google Gemini, local models, etc.) through an OpenAI-compatible API.

The dashboard tracks:
- Available AI models (181+ across all providers)
- New models since last check
- Latest frontier models from OpenAI, Anthropic, Google
- **Real-time spending and budget monitoring**
- **Historical spend data (time-series tracking)**
- **Team member activity and status**

**Key Features:**
- Single-user mode: Individual tracking with CBORG_API_KEY
- Team mode: Multi-user dashboard via team_keys.json
- Spend history: Automatic timestamped snapshots (up to 365 records)
- Activity monitoring: Last usage, key age, expiration, status
- Secure storage: Local JSON files indexed by API key hash

## Project Structure

```
.
├── dashboard.py              # Main dashboard application (Rich terminal UI)
├── cborg_api.py              # CBORG API client wrapper
├── storage.py                # Local JSON-based data storage with history tracking
├── test_api.py               # API testing/debugging script
├── run.sh                    # Convenience script to run dashboard
├── requirements.txt          # Python dependencies
├── team_keys.json            # Team API keys config (gitignored, created by user)
├── team_keys.json.template   # Template for team configuration
├── README.md                 # User documentation
├── CLAUDE.md                 # Developer/AI assistant documentation
└── .cborg_data/              # Local data storage (gitignored)
    ├── <key_hash>.json       # Per-key data files
    └── ...                   # One file per tracked API key
```

## Development Commands

### Setup
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Dashboard
```bash
# Set API key (required)
export CBORG_API_KEY=your-key-here

# Run dashboard (with venv)
source venv/bin/activate && python dashboard.py

# Or use convenience script
./run.sh
```

### Testing
```bash
# Test API endpoints
source venv/bin/activate && python test_api.py

# Test with different API key
CBORG_API_KEY=different-key python dashboard.py
```

## Architecture

### CBORG API
- **Base URL**: `https://api.cborg.lbl.gov`
- **Protocol**: OpenAI-compatible API
- **Authentication**: Bearer token via `CBORG_API_KEY` environment variable
- **Working Endpoints**:
  - `/v1/models` - List of available models (181+ models)
  - `/key/info` - Key information, spending, budget, status
- **Non-working Endpoints**:
  - `/user/info` returns 404
  - `/key/usage`, `/key/stats`, `/key/history` return 404
  - No per-model spend breakdown available (field exists but empty)

### Data Storage
- Files stored in `.cborg_data/<key_hash>.json`
- Key hash: First 16 chars of SHA-256 hash of API key
- One file per API key (supports multi-user tracking)
- Structure:
  ```json
  {
    "api_key_preview": "sk-XXXX...YYYY",
    "first_seen": "ISO8601 timestamp",
    "last_updated": "ISO8601 timestamp",
    "models": {
      "last_check": "ISO8601 timestamp",
      "known_models": ["model1", "model2", ...],
      "new_models": ["new_model1", ...]
    },
    "spend": {
      "last_check": "ISO8601 timestamp",
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

**Spend History Tracking:**
- Automatically records snapshots each dashboard run
- Only adds entry if spend changed (prevents duplicates)
- Stores up to 365 records (~1 year of daily checks)
- Enables future trend analysis and projections

### Dashboard UI (Rich library)
- Uses `rich` for terminal rendering
- Color-coded output:
  - Cyan: General info, headers
  - Green: LBL-hosted models (lbl/* prefix)
  - Yellow: New models, warnings
  - Red: Errors
- Tables with box styles (DOUBLE, ROUNDED, SIMPLE)
- Panels for organized sections

## Key Features

1. **Model Tracking**: Compares current model list against previously seen models to identify new additions
2. **Frontier Models**: Automatically curates top models from OpenAI (GPT-5, O-series), Anthropic (Opus/Sonnet 4.5), Google (Gemini 3 Pro)
3. **Multi-key Support**: Data indexed by API key hash allows tracking different keys separately
4. **Spend Monitoring**: Real-time tracking via `/key/info` endpoint with budget warnings
5. **Spend History**: Timestamped snapshots (up to 365 records) for trend analysis
6. **Team Mode**: Multi-user dashboard when `team_keys.json` exists
   - Individual spending per member
   - Activity monitoring (last usage, key age, status)
   - Aggregate team totals
   - Smart sorting (PI first, then by spend; activity by most recent)
7. **Relative Timestamps**: Shows "X days ago", "X hours ago" for last check times
8. **Security**: File permissions (600), gitignored secrets, API key hashing

## Common Tasks

### Adding New API Endpoints
Edit `cborg_api.py` → `CBORGClient` class. Follow OpenAI SDK patterns or use `requests` for custom endpoints.

### Modifying Dashboard UI
Edit `dashboard.py` → `CBORGDashboard` class. Use `rich` library components:
- `Table`: Structured data
- `Panel`: Grouped content with borders
- `Text`: Styled text with colors
- `Console`: Output rendering

### Changing Data Storage
Edit `storage.py` → `CBORGStorage` class. Currently uses JSON; could be migrated to SQLite or other formats.

## Dependencies

- **openai** (>=1.0.0): OpenAI-compatible API client
- **rich** (>=13.0.0): Terminal UI rendering
- **requests** (>=2.31.0): HTTP client for custom API calls
- **python-dateutil** (>=2.8.0): Date/time parsing and formatting

## Environment Variables

- `CBORG_API_KEY` (required): Your CBORG API key

## CBORG Service Details

- Web interface: https://cborg.lbl.gov
- API key management: https://api.cborg.lbl.gov/key/manage
- Documentation: https://cborg.lbl.gov/api_examples/
- Available models: https://cborg.lbl.gov/models/

### Model Categories
- **lbl/**: Lab-hosted open models (Llama, Qwen, DeepSeek, etc.)
- **openai/**: OpenAI models (GPT-4, GPT-5, O-series)
- **anthropic/**: Anthropic Claude models
- **google/**: Google Gemini models
- **xai/**: xAI Grok models
- **aws/**, **gcp/**, **azure/**: Cloud-provider-specific endpoints

## Troubleshooting

### Virtual Environment Issues
macOS/Linux uses externally-managed Python environments. Always use venv:
```bash
python3 -m venv venv
source venv/bin/activate
```

### API Authentication Errors
- Verify `CBORG_API_KEY` is set: `echo $CBORG_API_KEY`
- Check key format: Should start with `sk-`
- Test connection: `python test_api.py`

### Missing Dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

## Future Enhancements

With spend history now tracking, potential additions:

1. **Trend Visualization**
   - Graph spend over time
   - Daily/weekly burn rate calculations
   - Budget exhaustion projections

2. **Enhanced Analytics**
   - Usage spike detection
   - Team member comparisons
   - Cost optimization recommendations

3. **Export Capabilities**
   - CSV export for reporting (`--export csv`)
   - JSON export for external analysis
   - Monthly summary reports

4. **Alerting** (if needed)
   - Email/Slack notifications for budget thresholds
   - Inactive user warnings
   - Blocked key alerts

**Current Status:** Core functionality complete. Dashboard is production-ready. Historical data is accumulating automatically for future analysis.
