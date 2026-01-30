from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class Pph21Config:
    ptkp_map: dict[str, int]
    brackets: list[tuple[int, float]]
    no_npwp_multiplier: float


DEFAULT_PPH21_CONFIG = Pph21Config(
    ptkp_map={
        "TK0": 54_000_000,
        "TK1": 58_500_000,
        "TK2": 63_000_000,
        "TK3": 67_500_000,
        "K0": 58_500_000,
        "K1": 63_000_000,
        "K2": 67_500_000,
        "K3": 72_000_000,
    },
    brackets=[
        (60_000_000, 0.05),
        (250_000_000, 0.15),
        (500_000_000, 0.25),
        (5_000_000_000, 0.30),
        (10**18, 0.35),
    ],
    no_npwp_multiplier=1.2,
)


def _round_down_to_thousand(amount: float) -> int:
    value = int(amount or 0)
    return value - (value % 1_000)


def _compute_progressive_tax(pkp: int, brackets: list[tuple[int, float]]) -> float:
    remaining = int(max(0, pkp))
    tax = 0.0
    for cap, rate in brackets:
        if remaining <= 0:
            break
        chunk = min(remaining, int(cap))
        tax += float(chunk) * float(rate)
        remaining -= chunk
    return tax


def calculate_pph21(
    *,
    yearly_income: float,
    ptkp_status: str = "TK0",
    has_npwp: bool = True,
    config: Pph21Config = DEFAULT_PPH21_CONFIG,
) -> float:
    ptkp = int(config.ptkp_map.get(ptkp_status or "TK0", config.ptkp_map["TK0"]))
    pkp = _round_down_to_thousand(float(yearly_income or 0) - ptkp)
    tax = _compute_progressive_tax(pkp, config.brackets)
    if not bool(has_npwp):
        tax *= float(config.no_npwp_multiplier)
    return float(tax)


def policy_code_snippet() -> str:
    return (
        "from pph21_plugin.indonesia import calculate_pph21 as plugin_calculate_pph21\n"
        "\n"
        "def calculate_pph21(yearly_income, ptkp_status, has_npwp):\n"
        "    return plugin_calculate_pph21(yearly_income=yearly_income, ptkp_status=ptkp_status, has_npwp=has_npwp)\n"
    )

