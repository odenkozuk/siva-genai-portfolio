"""
Revenue field schema definitions and validation.
Defines the structured output expected from the extraction pipeline.
"""

from pydantic import BaseModel, Field
from typing import Optional


class RevenueFields(BaseModel):
    """Structured revenue fields extracted from financial/contract documents."""

    contract_id: Optional[str] = Field(None, description="Contract or agreement identifier")
    client_name: Optional[str] = Field(None, description="Client or customer name")
    vendor_name: Optional[str] = Field(None, description="Vendor or service provider name")

    contract_value: Optional[str] = Field(None, description="Total contract value (e.g. $1,200,000)")
    annual_revenue: Optional[str] = Field(None, description="Annual revenue figure")
    quarterly_revenue: Optional[str] = Field(None, description="Quarterly revenue figure")
    monthly_revenue: Optional[str] = Field(None, description="Monthly revenue figure")

    contract_start_date: Optional[str] = Field(None, description="Contract or billing start date")
    contract_end_date: Optional[str] = Field(None, description="Contract or billing end date")
    payment_terms: Optional[str] = Field(None, description="Payment terms (e.g. NET-30, milestone-based)")

    currency: Optional[str] = Field(None, description="Currency code (e.g. USD, EUR, INR)")
    revenue_type: Optional[str] = Field(None, description="Type of revenue (recurring, one-time, milestone)")
    billing_frequency: Optional[str] = Field(None, description="Billing cycle (monthly, quarterly, annual)")

    discount: Optional[str] = Field(None, description="Discount percentage or amount applied")
    tax_rate: Optional[str] = Field(None, description="Tax rate or GST/VAT details")
    net_revenue: Optional[str] = Field(None, description="Net revenue after deductions")

    project_name: Optional[str] = Field(None, description="Project or engagement name")
    cost_center: Optional[str] = Field(None, description="Cost center or department code")
    purchase_order: Optional[str] = Field(None, description="Purchase Order (PO) number")

    confidence_score: float = Field(0.0, description="Extraction confidence 0.0 to 1.0")
    source_page: Optional[int] = Field(None, description="Page number where data was found")
    extraction_notes: Optional[str] = Field(None, description="Notes or caveats about extraction")


REVENUE_KEYWORDS = [
    "revenue", "contract value", "total value", "annual value", "payment terms",
    "billing", "invoice", "amount", "fee", "cost", "price", "purchase order",
    "PO number", "net revenue", "gross revenue", "discount", "tax", "GST", "VAT",
    "recurring", "one-time", "milestone", "quarterly", "monthly", "annually",
]
