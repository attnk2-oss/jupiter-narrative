# JupiterNarrative 📊

**Know what's hot on Solana before everyone else.**

A real-time narrative heat tracker that monitors Solana token activity, maps it to narrative categories (AI, Meme, DeFi, etc.), and uses Jupiter Quote API to calculate optimal portfolio allocations for each narrative.

## What It Does

```
Token Market Data → Narrative Mapping → Heat Scoring → Jupiter Portfolio Optimization
```

1. **Monitors** 18+ Solana tokens across 5 narrative categories
2. **Scores** each token's "heat" based on price movement, volume, and momentum
3. **Ranks** narratives from "🔥🔥🔥 ON FIRE" to "❄️ Cold"
4. **Optimizes** portfolio allocation using Jupiter Quote API for best routing

## Quick Start

```bash
python3 run.py                     # Full narrative report
python3 run.py --top 3             # Top 3 narratives only
python3 run.py --portfolio 1.0     # Portfolio plan with 1 SOL budget
python3 run.py --narrative "AI"    # Focus on AI narrative
python3 run.py --watch --interval 30  # Continuous monitoring
python3 run.py --json              # JSON output for bots/agents
```

## Narrative Categories

| Narrative | Tokens | Description |
|-----------|--------|-------------|
| AI / DePIN | JUP, PYTH, DRIFT, TENSOR | AI and decentralized infrastructure |
| Meme / Culture | WIF, BONK, WEN | Memecoins and cultural tokens |
| DeFi / Infrastructure | JUP, RAY, ORCA, DRIFT, JITO | Core DeFi primitives |
| Liquid Staking | JITO, BSOL, MSOL, INF | Liquid staking derivatives |
| NFT / Social | TENSOR | NFT marketplace protocols |

## How It Works

### Heat Scoring
Each token gets a heat score (0-100) based on:
- **Price change** (24h): momentum indicator
- **Volume**: activity indicator
- **Volatility**: interest indicator

### Narrative Aggregation
Token heats are aggregated by narrative category:
- Average heat score per narrative
- Total volume per narrative
- Weighted 24h change

### Portfolio Optimization
For each narrative, Jupiter Quote API calculates:
- Optimal weight allocation (hotter tokens get more)
- Best swap routes (Raydium, Orca, Meteora, etc.)
- Price impact for each leg

## Architecture

```
jupiter-narrative/
├── jupiter_narrative/
│   ├── config.py             # Token registry, narrative definitions
│   ├── narrative_engine.py   # Heat scoring, narrative analysis
│   └── optimizer.py          # Jupiter portfolio optimization
├── run.py                    # CLI entry point
└── README.md
```

## APIs Used

| API | Purpose |
|-----|---------|
| **Jupiter Quote API** | Route optimization for portfolio allocation |
| **Jupiter Price API** | Real-time token prices |
| **CoinGecko API** | Market data (volume, market cap) |

### The "Oh" Factor

Jupiter's APIs are designed for **executing single swaps**. JupiterNarrative repurposes them as a **portfolio construction engine**:

1. **Narrative → Multi-Token Portfolio**: A single narrative ("Liquid Staking is hot") becomes a multi-token allocation plan with optimized Jupiter routes for each leg.

2. **Heat-Weighted Allocation**: Instead of equal weight, hotter tokens get proportionally more allocation — something no standard DCA or portfolio tool does.

3. **Real-Time Route Discovery**: Each rebalance fetches fresh Jupiter quotes, so the routing adapts to current liquidity conditions.

## For Production

```bash
# Live mode with real API data
python3 run.py --live --portfolio 2.0

# Continuous monitoring
python3 run.py --live --watch --interval 120
```

## Built For

**Superteam Earn — "Not Your Regular Bounty" (Jupiter Hackathon)**

> "Combine APIs in ways we didn't design for"

JupiterNarrative turns Jupiter's swap infrastructure into a **narrative intelligence system** — not just executing trades, but telling you *what* to trade based on market heat.

## License

MIT
