#!/usr/bin/env python3
"""
JupiterNarrative - Solana Narrative Heat Tracker

Usage:
    python3 run.py                  # Full narrative report
    python3 run.py --top 3          # Top 3 narratives only
    python3 run.py --portfolio 1.0  # Portfolio plan with 1 SOL budget
    python3 run.py --json           # JSON output
    python3 run.py --watch          # Continuous monitoring (every 60s)
"""

import sys
import json
import time
import argparse

from jupiter_narrative.config import Config
from jupiter_narrative.narrative_engine import NarrativeEngine
from jupiter_narrative.optimizer import PortfolioOptimizer, format_portfolio


BANNER = """
╔══════════════════════════════════════════════════════════╗
║         📊 JupiterNarrative Heat Tracker 📊              ║
║   Know what's hot on Solana before everyone else         ║
╚══════════════════════════════════════════════════════════╝
"""


def main():
    parser = argparse.ArgumentParser(description="Solana narrative heat tracker powered by Jupiter")
    parser.add_argument("--top", type=int, default=5, help="Show top N narratives")
    parser.add_argument("--portfolio", type=float, help="Generate portfolio plan with SOL budget")
    parser.add_argument("--narrative", type=str, help="Focus on specific narrative (e.g., 'AI / DePIN')")
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--watch", action="store_true", help="Continuous monitoring")
    parser.add_argument("--interval", type=int, default=60, help="Watch interval in seconds")
    parser.add_argument("--live", action="store_true", help="Use live Jupiter Quote API for portfolio routes")
    args = parser.parse_args()

    config = Config.from_env()
    engine = NarrativeEngine(config)
    optimizer = PortfolioOptimizer(config)

    if args.watch:
        print(BANNER)
        print(f"  Monitoring every {args.interval}s... (Ctrl+C to stop)\n")
        try:
            while True:
                print(f"\n{'='*55}")
                print(f"  ⏰ Update: {time.strftime('%Y-%m-%d %H:%M:%S')}")
                _run_report(engine, optimizer, args)
                time.sleep(args.interval)
        except KeyboardInterrupt:
            print("\n  👋 Stopped monitoring")
        return

    if not args.json:
        print(BANNER)

    _run_report(engine, optimizer, args)


def _run_report(engine, optimizer, args):
    narratives = engine.analyze_narratives()

    # Filter if specific narrative requested
    if args.narrative:
        narratives = [n for n in narratives if args.narrative.lower() in n.name.lower()]
        if not narratives:
            print(f"  ❌ Narrative '{args.narrative}' not found")
            return

    # Limit to top N
    narratives = narratives[:args.top]

    if args.json:
        output = []
        for n in narratives:
            output.append({
                "rank": n.rank, "name": n.name, "description": n.description,
                "avg_heat": round(n.avg_heat, 1), "avg_change_24h": round(n.avg_change_24h, 2),
                "total_volume": round(n.total_volume, 0), "status": n.status,
                "tokens": [{"symbol": t.symbol, "price": round(t.price_usd, 6),
                            "change_24h": round(t.price_change_24h, 2),
                            "heat": round(t.heat_score, 1), "trend": t.trend}
                           for t in t_sorted],
            })
        print(json.dumps(output, indent=2, ensure_ascii=False))
        return

    # Text report
    print(engine.get_narrative_report())

    # Portfolio plan if requested
    if args.portfolio:
        print(f"\n  💰 PORTFOLIO OPTIMIZER (Budget: {args.portfolio} SOL)")
        print(f"  {'═' * 50}")

        target_narratives = narratives[:3] if not args.narrative else narratives
        for n in target_narratives:
            plan = optimizer.optimize(n, args.portfolio)
            print(format_portfolio(plan))


if __name__ == "__main__":
    main()
