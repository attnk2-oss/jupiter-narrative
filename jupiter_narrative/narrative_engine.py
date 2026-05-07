"""
Narrative Heat Engine (Production Grade)

Uses REAL market data from CoinGecko API (free, no key required).
Heat scoring based on actual price movement, volume, and market dynamics.
No mock data, no random numbers.
"""

import json
import ssl
import os
import time
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request, ProxyHandler, build_opener
from urllib.error import HTTPError

from .config import Config, NARRATIVES, TOKEN_META, get_symbol

# HTTP setup
_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy") or os.getenv("HTTPS_PROXY") or os.getenv("https_proxy")
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE
_opener = None
if _proxy:
    _opener = build_opener(ProxyHandler({"http": _proxy, "https": _proxy}))


def _api_get(url: str, timeout: int = 15) -> dict:
    req = Request(url, headers={
        "Accept": "application/json",
        "User-Agent": "JupiterNarrative/0.1",
    })
    try:
        if _opener:
            resp = _opener.open(req, timeout=timeout)
        else:
            resp = urlopen(req, timeout=timeout, context=_ssl_ctx)
        with resp:
            return json.loads(resp.read().decode())
    except HTTPError as e:
        raise RuntimeError(f"API {e.code}: {e.read().decode()[:200]}") from e


# CoinGecko ID mapping (symbol -> coingecko_id)
COINGECKO_IDS = {
    "SOL": "solana", "JUP": "jupiter-exchange-solana", "RAY": "raydium",
    "ORCA": "orca", "JITO": "jito-governance-token",
    "DRIFT": "drift-protocol", "WIF": "dogwifhat",
    "BONK": "bonk", "PYTH": "pyth-network",
    "TENSOR": "tensor", "KMNO": "kamino",
    "WEN": "wen-4", "MNGO": "mango-markets",
    "BSOL": "blazestake-staked-sol", "MSOL": "marinade",
    "INF": "sanctum-2",
}


@dataclass
class TokenHeat:
    """Real heat data for a single token from CoinGecko."""
    mint: str
    symbol: str
    coingecko_id: str
    price_usd: float
    volume_24h: float
    price_change_24h: float
    price_change_7d: float
    market_cap: float
    market_cap_rank: int
    heat_score: float  # 0-100, calculated from real data

    @property
    def trend(self) -> str:
        if self.price_change_24h > 15:
            return "🔥 Explosive"
        elif self.price_change_24h > 5:
            return "🔥 Hot"
        elif self.price_change_24h > 1:
            return "📈 Rising"
        elif self.price_change_24h > -1:
            return "➡️ Flat"
        elif self.price_change_24h > -5:
            return "📉 Declining"
        else:
            return "❄️ Cold"

    @property
    def volume_mcap_ratio(self) -> float:
        """Volume/MarketCap ratio - higher = more活跃."""
        if self.market_cap > 0:
            return self.volume_24h / self.market_cap
        return 0


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
        elif self.avg_heat > 40:
            return "🔥 Warm"
        elif self.avg_heat > 25:
            return "😐 Neutral"
        else:
            return "❄️ Cold"

    @property
    def top_token(self) -> Optional[TokenHeat]:
        if self.tokens:
            return max(self.tokens, key=lambda t: t.heat_score)
        return None


class NarrativeEngine:
    """Detect and rank Solana narratives using real market data."""

    def __init__(self, config: Optional[Config] = None):
        self.config = config or Config()
        self._cache: dict[str, TokenHeat] = {}
        self._cache_time: float = 0
        self._cache_ttl: float = 300  # 5 min cache

    def _fetch_market_data(self) -> dict[str, dict]:
        """Fetch real market data from CoinGecko."""
        # Get all CoinGecko IDs we need
        ids = list(set(COINGECKO_IDS.values()))
        ids_str = ",".join(ids)

        url = (
            f"https://api.coingecko.com/api/v3/coins/markets"
            f"?vs_currency=usd"
            f"&ids={ids_str}"
            f"&order=market_cap_desc"
            f"&per_page=50"
            f"&sparkline=false"
            f"&price_change_percentage=24h,7d"
        )

        data = _api_get(url)

        # Map by symbol
        result = {}
        for coin in data:
            cg_id = coin.get("id", "")
            # Find matching symbol
            for sym, cid in COINGECKO_IDS.items():
                if cid == cg_id:
                    result[sym] = coin
                    break

        return result

    def _calculate_heat(self, coin: dict) -> float:
        """
        Calculate heat score (0-100) from real market data.

        Factors:
        - Price change 24h (40% weight): momentum
        - Volume/MarketCap ratio (30% weight): activity
        - Price change 7d (20% weight): trend
        - Market cap rank (10% weight): prominence
        """
        change_24h = coin.get("price_change_percentage_24h", 0) or 0
        change_7d = coin.get("price_change_percentage_24h_in_currency", 0) or 0
        volume = coin.get("total_volume", 0) or 0
        mcap = coin.get("market_cap", 0) or 0
        rank = coin.get("market_cap_rank", 100) or 100

        # Normalize each factor to 0-100
        # Price change: -30% to +30% maps to 0-100
        momentum_score = max(0, min(100, (change_24h + 30) * (100 / 60)))

        # Volume/MCap ratio: 0 to 0.3 maps to 0-100
        vol_ratio = volume / mcap if mcap > 0 else 0
        activity_score = max(0, min(100, vol_ratio * (100 / 0.3)))

        # 7d trend: -50% to +50% maps to 0-100
        trend_score = max(0, min(100, (change_7d + 50) * (100 / 100)))

        # Market cap rank: rank 1 = 100, rank 200 = 0
        prominence_score = max(0, min(100, 100 - (rank / 2)))

        # Weighted average
        heat = (
            momentum_score * 0.40 +
            activity_score * 0.30 +
            trend_score * 0.20 +
            prominence_score * 0.10
        )

        return round(heat, 1)

    def get_token_heat(self, symbol: str) -> Optional[TokenHeat]:
        """Get heat data for a single token using real market data."""
        # Check cache
        if time.time() - self._cache_time < self._cache_ttl and symbol in self._cache:
            return self._cache[symbol]

        # Fetch all data at once (efficient)
        if time.time() - self._cache_time >= self._cache_ttl:
            self._refresh_cache()

        return self._cache.get(symbol)

    def _refresh_cache(self):
        """Refresh all token data from CoinGecko."""
        try:
            market_data = self._fetch_market_data()
        except Exception as e:
            print(f"  ⚠️ CoinGecko fetch failed: {e}", file=__import__('sys').stderr)
            return

        for sym, cg_id in COINGECKO_IDS.items():
            coin = market_data.get(sym)
            if not coin:
                continue

            mint = self.config.token_registry.get(sym, "")
            heat = self._calculate_heat(coin)

            self._cache[sym] = TokenHeat(
                mint=mint, symbol=sym, coingecko_id=cg_id,
                price_usd=coin.get("current_price", 0) or 0,
                volume_24h=coin.get("total_volume", 0) or 0,
                price_change_24h=coin.get("price_change_percentage_24h", 0) or 0,
                price_change_7d=coin.get("price_change_percentage_24h_in_currency", 0) or 0,
                market_cap=coin.get("market_cap", 0) or 0,
                market_cap_rank=coin.get("market_cap_rank", 0) or 0,
                heat_score=heat,
            )

        self._cache_time = time.time()

    def analyze_narratives(self) -> list[NarrativeHeat]:
        """Analyze all narratives using real market data."""
        # Ensure cache is fresh
        if time.time() - self._cache_time >= self._cache_ttl:
            self._refresh_cache()

        results = []

        for name, info in NARRATIVES.items():
            token_heats = []
            for sym in info["tokens"]:
                heat = self._cache.get(sym)
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

        results.sort(key=lambda x: x.avg_heat, reverse=True)
        for i, r in enumerate(results):
            r.rank = i + 1

        return results

    def get_narrative_report(self) -> str:
        """Generate a formatted narrative heat report from real data."""
        narratives = self.analyze_narratives()

        lines = []
        lines.append("=" * 55)
        lines.append("  📊 SOLANA NARRATIVE HEAT MAP (LIVE DATA)")
        lines.append("  Data: CoinGecko API | Powered by JupiterNarrative")
        lines.append("=" * 55)
        lines.append("")

        for n in narratives:
            top = n.top_token
            top_str = f" | Leader: {top.symbol} ({top.price_change_24h:+.1f}%)" if top else ""
            lines.append(f"  #{n.rank} {n.name}  {n.status}{top_str}")
            lines.append(f"     {n.description}")
            lines.append(f"     Avg Heat: {n.avg_heat:.0f}/100 | 24h: {n.avg_change_24h:+.1f}% | Vol: ${n.total_volume/1e6:.0f}M")
            lines.append(f"     Tokens:")
            for t in sorted(n.tokens, key=lambda x: x.heat_score, reverse=True):
                lines.append(
                    f"       {t.symbol:>6}: ${t.price_usd:.4f} ({t.price_change_24h:+.1f}%) "
                    f"{t.trend} [heat:{t.heat_score:.0f}] [vol:${t.volume_24h/1e6:.0f}M]"
                )
            lines.append("")

        if narratives:
            top = narratives[0]
            lines.append("─" * 55)
            lines.append(f"  🎯 HOTTEST NARRATIVE: {top.name}")
            if top.tokens:
                sorted_tokens = sorted(top.tokens, key=lambda x: x.heat_score, reverse=True)
                lines.append(f"     Top tokens: {', '.join(t.symbol for t in sorted_tokens[:3])}")
            lines.append("")

        return "\n".join(lines)
