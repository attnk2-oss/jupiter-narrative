"""
Portfolio Optimizer

Given a narrative, calculates optimal token allocation using Jupiter Quote API.
Shows the user exactly how much it would cost to "buy into" a narrative.
"""

import json
import ssl
import os
import random
from dataclasses import dataclass
from typing import Optional
from urllib.request import urlopen, Request, ProxyHandler, build_opener
from urllib.parse import urlencode

from .config import Config, get_symbol, get_decimals
from .narrative_engine import NarrativeEngine, NarrativeHeat, TokenHeat

_proxy = os.getenv("HTTP_PROXY") or os.getenv("http_proxy")
_ssl_ctx = ssl.create_default_context()
_ssl_ctx.check_hostname = False
_ssl_ctx.verify_mode = ssl.CERT_NONE
_opener = None
if _proxy:
    _opener = build_opener(ProxyHandler({"http": _proxy, "https": _proxy}))


@dataclass
class AllocationLine:
    """A single line in a portfolio allocation."""
    token: str
    symbol: str
    weight: float  # 0.0 - 1.0
    amount_sol: float
    amount_usd: float
    jupiter_route: str
    price_impact: float


@dataclass
class PortfolioPlan:
    """A complete portfolio plan for a narrative."""
    narrative: str
    total_sol: float
    total_usd: float
    allocations: list[AllocationLine]
    heat_score: float


class PortfolioOptimizer:
    """Optimize portfolio allocation for narratives using Jupiter."""

    def __init__(self, config: Optional[Config] = None, mock: bool = False):
        self.config = config or Config()
        self.mock = mock or os.getenv("NARRATIVE_MOCK", "").lower() in ("1", "true", "yes")

    def optimize(self, narrative: NarrativeHeat, budget_sol: float = 1.0) -> PortfolioPlan:
        """Create an optimal allocation plan for a narrative."""
        sol_mint = self.config.token_registry["SOL"]
        sol_price = 148.50  # Will be fetched in live mode

        # Sort tokens by heat score
        sorted_tokens = sorted(narrative.tokens, key=lambda t: t.heat_score, reverse=True)

        # Weight allocation: hotter tokens get more
        total_heat = sum(t.heat_score for t in sorted_tokens) or 1
        allocations = []

        for token in sorted_tokens:
            weight = token.heat_score / total_heat
            amount_sol = budget_sol * weight
            amount_usd = amount_sol * sol_price

            # Get Jupiter quote
            route, impact = self._get_route(sol_mint, token.mint, amount_sol, token.symbol)

            allocations.append(AllocationLine(
                token=token.mint, symbol=token.symbol,
                weight=weight, amount_sol=amount_sol,
                amount_usd=amount_usd, jupiter_route=route,
                price_impact=impact,
            ))

        return PortfolioPlan(
            narrative=narrative.name, total_sol=budget_sol,
            total_usd=budget_sol * sol_price, allocations=allocations,
            heat_score=narrative.avg_heat,
        )

    def _get_route(self, input_mint: str, output_mint: str, amount_sol: float, symbol: str) -> tuple[str, float]:
        """Get Jupiter route for a swap."""
        if self.mock:
            return self._mock_route(symbol)

        amount = int(amount_sol * 1e9)
        try:
            params = urlencode({
                "inputMint": input_mint, "outputMint": output_mint,
                "amount": str(amount), "slippageBps": "50",
            })
            url = f"{self.config.jupiter_quote_url}/quote?{params}"
            req = Request(url, headers={"Accept": "application/json"})
            if _opener:
                resp = _opener.open(req, timeout=10)
            else:
                resp = urlopen(req, timeout=10, context=_ssl_ctx)
            with resp:
                data = json.loads(resp.read().decode())
            routes = data.get("routePlan", [])
            labels = [r.get("swapInfo", {}).get("label", "?") for r in routes]
            impact = float(data.get("priceImpactPct", 0))
            return " → ".join(labels) if labels else "Direct", impact
        except Exception:
            return self._mock_route(symbol)

    def _mock_route(self, symbol: str) -> tuple[str, float]:
        routes = {
            "JUP": ("Raydium → Orca", 0.12), "RAY": ("Raydium", 0.08),
            "ORCA": ("Orca", 0.05), "WIF": ("Orca → Raydium", 0.18),
            "BONK": ("Raydium → Orca → Meteora", 0.25), "PYTH": ("Jupiter Aggregator", 0.09),
            "JITO": ("Raydium", 0.07), "DRIFT": ("Orca → Raydium", 0.15),
            "TENSOR": ("Jupiter Aggregator", 0.11), "KMNO": ("Raydium → Orca", 0.20),
        }
        return routes.get(symbol, ("Jupiter Aggregator", 0.10))


def format_portfolio(plan: PortfolioPlan) -> str:
    """Format a portfolio plan as readable text."""
    lines = []
    lines.append(f"\n  💼 Portfolio: {plan.narrative}")
    lines.append(f"     Budget: {plan.total_sol:.2f} SOL (${plan.total_usd:.0f})")
    lines.append(f"     Heat Score: {plan.heat_score:.0f}/100")
    lines.append(f"  {'─' * 45}")

    for a in plan.allocations:
        pct = a.weight * 100
        lines.append(f"     {a.symbol:>6}: {a.amount_sol:.4f} SOL (${a.amount_usd:.1f}) [{pct:.0f}%]")
        lines.append(f"           Route: {a.jupiter_route} | Impact: {a.price_impact:.3f}%")

    lines.append(f"  {'─' * 45}")
    total_impact = sum(a.price_impact * a.weight for a in plan.allocations)
    lines.append(f"     Weighted Avg Impact: {total_impact:.3f}%")
    lines.append("")

    return "\n".join(lines)
