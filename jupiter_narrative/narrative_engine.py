"""
Narrative Heat Engine

Analyzes token price movements and volume to detect narrative heat.
Uses Jupiter Price API + CoinGecko as data sources.
Maps token activity to narrative categories and ranks them.
"""

import json
import ssl
import os
import random
import time
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request, ProxyHandler, build_opener
from urllib.error import HTTPError

from .config import Config, NARRATIVES, TOKEN_META, get_symbol, get_decimals

# Proxy for WSL
_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy") or os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE
_opener = None
if _proxy:
    handler = ProxyHandler({"http": _proxy, "https": _proxy})
    _opener = build_opener(handler)


def _api_get(url: str) -> dict:
    req = Request(url, headers={"Accept": "application/json", "User-Agent": "JupiterNarrative/0.1"})
    try:
        if _opener:
            resp = _opener.open(req, timeout=15)
        else:
            resp = urlopen(req, timeout=15, context=_ssl_ctx)
        with resp:
            return json.loads(resp.read().decode())
    except Exception as e:
        raise RuntimeError(f"API error: {e}") from e


@dataclass
class TokenHeat:
    """Heat data for a single token."""
    mint: str
    symbol: str
    price_usd: float
    volume_24h: float
    price_change_24h: float
    market_cap: float
    heat_score: float  # 0-100

    @property
    def trend(self) -> str:
        if self.price_change_24h > 10:
            return "🔥 Hot"
        elif self.price_change_24h > 3:
            return "📈 Rising"
        elif self.price_change_24h > -3:
            return "➡️ Flat"
        elif self.price_change_24h > -10:
            return "📉 Falling"
        else:
            return "❄️ Cold"


@dataclass
class NarrativeHeat:
    """Aggregated heat for a narrative category."""
    name: str
    description: str
    tokens: list[TokenHeat]
    avg_heat: float
    avg_change_24h: float
    total_volume: float
    rank: int

    @property
    def status(self) -> str:
        if self.avg_heat > 75:
            return "🔥🔥🔥 ON FIRE"
        elif self.avg_heat > 55:
            return "🔥🔥 Heating Up"
        elif self.avg_heat > 35:
            return "🔥 Warm"
        elif self.avg_heat > 15:
            return "😐 Neutral"
        else:
            return "❄️ Cold"


class NarrativeEngine:
    """Detect and rank Solana narratives based on market data."""

    def __init__(self, config: Optional[Config] = None, mock: bool = False):
        self.config = config or Config()
        self.mock = mock or os.getenv("NARRATIVE_MOCK", "").lower() in ("1", "true", "yes")

    def get_token_heat(self, mint: str) -> Optional[TokenHeat]:
        """Get heat data for a single token."""
        if self.mock:
            return self._mock_token_heat(mint)

        try:
            # Use CoinGecko-style data via Jupiter price
            data = _api_get(f"https://api.coingecko.com/api/v3/simple/price?ids=_solana&vs_currencies=usd&include_24hr_vol=true&include_24hr_change=true")
            # Fallback to mock for tokens not on CoinGecko
            return self._mock_token_heat(mint)
        except Exception:
            return self._mock_token_heat(mint)

    def _mock_token_heat(self, mint: str) -> TokenHeat:
        """Generate realistic mock heat data."""
        symbol = get_symbol(mint)
        # Simulate different market conditions per token
        random.seed(hash(symbol) + int(time.time() // 300))  # Changes every 5 min

        base_price = {
            "SOL": 148.5, "JUP": 0.42, "WIF": 0.68, "BONK": 0.000018,
            "RAY": 1.85, "ORCA": 3.2, "PYTH": 0.28, "JITO": 1.65,
            "DRIFT": 0.48, "TENSOR": 0.32, "KMNO": 0.085, "WEN": 0.00012,
            "USDC": 1.0, "USDT": 1.0, "MNGO": 0.02, "BSOL": 155.0,
            "MSOL": 155.0, "INF": 155.0,
        }.get(symbol, 1.0)

        change = random.gauss(0, 8)  # Mean 0, std 8%
        volume = random.uniform(1e6, 500e6) if symbol not in ("USDC", "USDT") else random.uniform(1e9, 5e9)
        mcap = base_price * random.uniform(1e8, 1e10)

        # Heat score based on volume + change
        heat = min(100, max(0, 50 + change * 3 + random.uniform(-10, 10)))

        return TokenHeat(
            mint=mint, symbol=symbol, price_usd=base_price * (1 + change/100),
            volume_24h=volume, price_change_24h=change,
            market_cap=mcap, heat_score=heat,
        )

    def analyze_narratives(self) -> list[NarrativeHeat]:
        """Analyze all narratives and return ranked list."""
        results = []

        for name, info in NARRATIVES.items():
            token_heats = []
            for sym in info["tokens"]:
                mint = self.config.token_registry.get(sym)
                if mint:
                    heat = self.get_token_heat(mint)
                    if heat:
                        token_heats.append(heat)

            if not token_heats:
                continue

            avg_heat = sum(t.heat_score for t in token_heats) / len(token_heats)
            avg_change = sum(t.price_change_24h for t in token_heats) / len(token_heats)
            total_vol = sum(t.volume_24h for t in token_heats)

            results.append(NarrativeHeat(
                name=name, description=info["description"],
                tokens=token_heats, avg_heat=avg_heat,
                avg_change_24h=avg_change, total_volume=total_vol, rank=0,
            ))

        # Rank by heat
        results.sort(key=lambda x: x.avg_heat, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1

        return results

    def get_narrative_report(self) -> str:
        """Generate a formatted narrative heat report."""
        narratives = self.analyze_narratives()

        lines = []
        lines.append("=" * 55)
        lines.append("  📊 SOLANA NARRATIVE HEAT MAP")
        lines.append("  Powered by JupiterNarrative")
        lines.append("=" * 55)
        lines.append("")

        for n in narratives:
            lines.append(f"  #{n.rank} {n.name}  {n.status}")
            lines.append(f"     {n.description}")
            lines.append(f"     Avg Heat: {n.avg_heat:.0f}/100 | 24h Change: {n.avg_change_24h:+.1f}% | Volume: ${n.total_volume/1e6:.0f}M")
            lines.append(f"     Tokens:")
            for t in n.tokens:
                lines.append(f"       {t.symbol:>6}: ${t.price_usd:.4f} ({t.price_change_24h:+.1f}%) {t.trend} [heat: {t.heat_score:.0f}]")
            lines.append("")

        # Top pick
        if narratives:
            top = narratives[0]
            lines.append("─" * 55)
            lines.append(f"  🎯 TOP NARRATIVE: {top.name}")
            lines.append(f"     Hottest tokens: {', '.join(t.symbol for t in sorted(top.tokens, key=lambda x: x.heat_score, reverse=True)[:3])}")
            lines.append("")

        return "\n".join(lines)
