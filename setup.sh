#!/usr/bin/env bash
# ============================================================
# Networking Jobs Search System - Setup Script
# ============================================================
set -e

echo "======================================================"
echo "  Networking Jobs Search System Setup"
echo "======================================================"

# ── Check Python ────────────────────────────────────────────
if ! command -v python3 &>/dev/null; then
    echo "ERROR: Python 3 is required. Install it first."
    exit 1
fi

PYTHON=$(command -v python3)
echo "Using Python: $PYTHON"

# ── Create virtual environment ──────────────────────────────
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    $PYTHON -m venv venv
fi

source venv/bin/activate

# ── Install dependencies ────────────────────────────────────
echo "Installing dependencies..."
pip install --upgrade pip -q
pip install -r requirements.txt -q

# ── Initialize database ─────────────────────────────────────
echo "Initializing database..."
python3 -c "import database; database.init_db(); print('Database ready.')"

# ── Linux: Install libnotify for desktop notifications ──────
if command -v apt-get &>/dev/null; then
    echo "Installing libnotify-bin for desktop notifications..."
    apt-get install -y libnotify-bin 2>/dev/null || true
fi

echo ""
echo "======================================================"
echo "  SETUP COMPLETE!"
echo "======================================================"
echo ""
echo "  To start the Command Center (interactive UI):"
echo "    source venv/bin/activate"
echo "    python command_center.py"
echo ""
echo "  To run the scheduler (morning/evening notifications):"
echo "    source venv/bin/activate"
echo "    python scheduler.py"
echo ""
echo "  To run a single scrape:"
echo "    source venv/bin/activate"
echo "    python scheduler.py --once"
echo ""
echo "  To add to crontab (auto-run daily):"
echo "    crontab -e"
echo "    # Add these lines:"
echo "    0 7  * * * cd $(pwd) && source venv/bin/activate && python scheduler.py --once"
echo "    0 8  * * * cd $(pwd) && source venv/bin/activate && python scheduler.py morning"
echo "    0 18 * * * cd $(pwd) && source venv/bin/activate && python scheduler.py evening"
echo ""
