from pydantic import BaseModel

from application.sales.queries.analytics import (
    DealFunnelResult,
    DealSummaryResult,
)


class DealSummaryResponseSchema(BaseModel):
    total_count: int
    new_count: int
    in_progress_count: int
    won_count: int
    lost_count: int
    total_won_amount: float
    new_deals_count: int | None = None

    @classmethod
    def from_result(cls, result: DealSummaryResult) -> "DealSummaryResponseSchema":
        return cls(
            total_count=result.total_count,
            new_count=result.new_count,
            in_progress_count=result.in_progress_count,
            won_count=result.won_count,
            lost_count=result.lost_count,
            total_won_amount=result.total_won_amount,
            new_deals_count=result.new_deals_count,
        )


class DealFunnelResponseSchema(BaseModel):
    qualification_count: int
    proposal_count: int
    negotiation_count: int
    closed_count: int

    @classmethod
    def from_result(cls, result: DealFunnelResult) -> "DealFunnelResponseSchema":
        return cls(
            qualification_count=result.qualification_count,
            proposal_count=result.proposal_count,
            negotiation_count=result.negotiation_count,
            closed_count=result.closed_count,
        )
