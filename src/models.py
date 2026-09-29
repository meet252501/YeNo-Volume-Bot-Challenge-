"""
Pydantic models for the /decide contract. Working copy reconstructed
from the challenge page's published example — see docs/data_schema.md
for open questions to verify against the real evaluator contract.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class MarketInfo(BaseModel):
    id: str
    secondsToClose: float


class Position(BaseModel):
    outcome: Literal["YES", "NO"]
    shares: float
    notional_paid: float


class AccountState(BaseModel):
    cashUsd: float
    eligibleVolumeUsd: float
    position: Position | None = None


class Rules(BaseModel):
    maximumBuyCashUsd: float
    targetVolumeUsd: float
    evaluationWindowHours: float


class ReferenceData(BaseModel):
    btcMidUsd: float
    openingTargetUsd: float
    observedAt: float
    targetObservedAt: float
    targetProvisional: bool


class BookSide(BaseModel):
    bids: list[list[float]]  # [[price, size], ...]
    asks: list[list[float]]


class OrderBooks(BaseModel):
    YES: BookSide
    NO: BookSide


class DecideRequest(BaseModel):
    market: MarketInfo
    account: AccountState
    rules: Rules
    reference: ReferenceData
    books: OrderBooks


class HoldAction(BaseModel):
    action: Literal["HOLD"] = "HOLD"


class BuyAction(BaseModel):
    action: Literal["BUY"] = "BUY"
    outcome: Literal["YES", "NO"]
    maxCashUsd: float


class SellAction(BaseModel):
    action: Literal["SELL"] = "SELL"


DecideResponse = HoldAction | BuyAction | SellAction
