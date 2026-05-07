"""Configuration and token registry."""

import os
from dataclasses import dataclass, field


@dataclass
class Config:
    solana_rpc: str = os.getenv("SOLANA_RPC_URL", "https://api.mainnet-beta.solana.io")
    jupiter_quote_url: str = "https://quote-api.jup.ag/v6"
    jupiter_price_url: str = "https://price.jup.ag/v6"

    token_registry: dict = field(default_factory=lambda: {
        "SOL": "So11111111111111111111111111111111",
        "USDC": "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        "USDT": "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        "JUP": "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN",
        "WIF": "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm",
        "BONK": "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263",
        "RAY": "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R",
        "ORCA": "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE",
        "PYTH": "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3",
        "JITO": "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL",
        "DRIFT": "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7",
        "TENSOR": "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6",
        "KMNO": "KMNo3nJsBXfcpJTVhZcXLW7RtbTom6S1JF1RnExvcec",
        "WEN": "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk",
        "MNGO": "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac",
        "BSOL": "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1",
        "MSOL": "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So",
        "INF": "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm",
    })

    @classmethod
    def from_env(cls) -> "Config":
        return cls()


# Narrative mapping: narrative -> relevant tokens
NARRATIVES = {
    "AI / DePIN": {
        "tokens": ["JUP", "PYTH", "DRIFT", "TENSOR"],
        "description": "Artificial Intelligence and Decentralized Physical Infrastructure",
        "weight": 1.0,
    },
    "Meme / Culture": {
        "tokens": ["WIF", "BONK", "WEN"],
        "description": "Memecoins and cultural tokens on Solana",
        "weight": 0.8,
    },
    "DeFi / Infrastructure": {
        "tokens": ["JUP", "RAY", "ORCA", "DRIFT", "JITO"],
        "description": "Core DeFi primitives and infrastructure",
        "weight": 1.0,
    },
    "Liquid Staking": {
        "tokens": ["JITO", "BSOL", "MSOL", "INF"],
        "description": "Liquid staking derivatives and MEV",
        "weight": 0.7,
    },
    "NFT / Social": {
        "tokens": ["TENSOR"],
        "description": "NFT marketplace and social protocols",
        "weight": 0.5,
    },
}


TOKEN_META = {
    "So11111111111111111111111111111111": {"symbol": "SOL", "name": "Solana", "decimals": 9},
    "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v": {"symbol": "USDC", "name": "USD Coin", "decimals": 6},
    "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB": {"symbol": "USDT", "name": "Tether USD", "decimals": 6},
    "JUPyiwrYJFskUPiHa7hkeR8VUtAeFoSYbKedZNsDvCN": {"symbol": "JUP", "name": "Jupiter", "decimals": 6},
    "EKpQGSJtjMFqKZ9KQanSqYXRcF8fBopzLHYxdM65zcjm": {"symbol": "WIF", "name": "dogwifhat", "decimals": 6},
    "DezXAZ8z7PnrnRJjz3wXBoRgixCa6xjnB7YaB1pPB263": {"symbol": "BONK", "name": "Bonk", "decimals": 5},
    "4k3Dyjzvzp8eMZWUXbBCjEvwSkkk59S5iCNLY3QrkX6R": {"symbol": "RAY", "name": "Raydium", "decimals": 6},
    "orcaEKTdK7LKz57vaAYr9QeNsVEPfiu6QeMU1kektZE": {"symbol": "ORCA", "name": "Orca", "decimals": 6},
    "HZ1JovNiVvGrGNiiYvEozEVgZ58xaU3RKwX8eACQBCt3": {"symbol": "PYTH", "name": "Pyth Network", "decimals": 6},
    "jtojtomepa8beP8AuQc6eXt5FriJwfFMwQx2v2f9mCL": {"symbol": "JITO", "name": "Jito", "decimals": 6},
    "DriFtupJYLTosbwoN8koMbEYSx54aFAVLddWsbksjwg7": {"symbol": "DRIFT", "name": "Drift Protocol", "decimals": 6},
    "TNSRxcUxoT9xBG3de7PiJyTDYu7kskLqcpddxnEJAS6": {"symbol": "TENSOR", "name": "Tensor", "decimals": 6},
    "KMNo3nJsBXfcpJTVhZcXLW7RtbTom6S1JF1RnExvcec": {"symbol": "KMNO", "name": "Kamino", "decimals": 6},
    "WENWENvqqNya429ubCdR81ZmD69brwQaaBYY6p3LCpk": {"symbol": "WEN", "name": "Wen", "decimals": 5},
    "MangoCzJ36AjZyKwVj3VnYU4GTonjfVEnJmvvWaxLac": {"symbol": "MNGO", "name": "Mango", "decimals": 6},
    "bSo13r4TkiE4KumL71LsHTPpL2euBYLFx6h9HP3piy1": {"symbol": "BSOL", "name": "blazeSOL", "decimals": 9},
    "mSoLzYCxHdYgdzU16g5QSh3i5K3z3KZK7ytfqcJm7So": {"symbol": "MSOL", "name": "Marinade SOL", "decimals": 9},
    "5oVNBeEEQvYi1cX3ir8Dx5n1P7pdxydbGF2X4TxVusJm": {"symbol": "INF", "name": "Infinity", "decimals": 9},
}


def get_symbol(mint: str) -> str:
    meta = TOKEN_META.get(mint)
    return meta["symbol"] if meta else mint[:6] + "..." + mint[-4:]

def get_decimals(mint: str) -> int:
    meta = TOKEN_META.get(mint)
    return meta["decimals"] if meta else 6
