from pydantic import BaseModel, Field
from datetime import datetime, date
from typing import Optional, List, Dict, Any, Union
from decimal import Decimal

# === COST ANALYSIS SCHEMAS ===

class CostSummary(BaseModel):
    """Cost Summary"""
    total_spent: Decimal = Field(..., description="Total spent")
    period_start: date = Field(..., description="Period start")
    period_end: date = Field(..., description="Period end")
    transaction_count: int = Field(..., description="Number of transactions")
    average_per_transaction: Decimal = Field(..., description="Average per transaction")

class VehicleCostSummary(BaseModel):
    """Vehicle Cost Summary"""
    vehicle_id: str
    vehicle_name: str  # "Toyota Camry 2020"
    license_plate: str
    total_spent: Decimal
    maintenance_cost: Decimal
    appointment_cost: Decimal
    transaction_count: int
    last_service_date: Optional[datetime] = None
    cost_per_km: Optional[Decimal] = None  # If mileage is available

class CategoryCostBreakdown(BaseModel):
    """Cost breakdown by category"""
    category: str  # "Oil change", "Brakes", "Tires", etc.
    total_cost: Decimal
    transaction_count: int
    percentage_of_total: float
    average_cost: Decimal
    last_service_date: Optional[datetime] = None

class MonthlySpending(BaseModel):
    """monthly expenses"""
    month: str  # "2024-01", "2024-02"
    total_spent: Decimal
    maintenance_cost: Decimal
    appointment_cost: Decimal
    transaction_count: int

class CostAnalyticsResponse(BaseModel):
    """Complete cost analytics response"""
    user_id: str
    period_summary: CostSummary
    vehicles: List[VehicleCostSummary]
    categories: List[CategoryCostBreakdown]
    monthly_spending: List[MonthlySpending]
    most_expensive_service: Optional[Dict[str, Any]] = None
    cost_trends: Dict[str, Union[str, float]]  # {"trend": "increasing", "change_percentage": 15.5}

class BudgetComparison(BaseModel):
    """Comparison with budget"""
    budget_amount: Optional[Decimal] = None
    actual_spent: Decimal
    difference: Decimal  # budget - actual (positive = under budget)
    percentage_used: float
    is_over_budget: bool
    days_remaining: int
    projected_monthly_spend: Decimal

class CostFilters(BaseModel):
    """Filters for cost queries"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    vehicle_ids: Optional[List[str]] = None
    categories: Optional[List[str]] = None
    min_amount: Optional[Decimal] = None
    max_amount: Optional[Decimal] = None

# === BUDGET MANAGEMENT ===

class BudgetCreate(BaseModel):
    """Create quote"""
    monthly_budget: Decimal = Field(..., gt=0, description="Monthly budget")
    vehicle_id: Optional[str] = None
    category: Optional[str] = None
    year: int = Field(..., ge=2020, le=2030)
    month: int = Field(..., ge=1, le=12)

class BudgetUpdate(BaseModel):
    """Update budget"""
    monthly_budget: Optional[Decimal] = Field(None, gt=0)
    is_active: Optional[bool] = None

class BudgetResponse(BaseModel):
    """Budget response"""
    id: str
    user_id: str
    monthly_budget: Decimal
    vehicle_id: Optional[str] = None
    category: Optional[str] = None
    year: int
    month: int
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True

# === REPORTING SCHEMAS ===

class ExpenseReport(BaseModel):
    """Detailed expense report"""
    report_id: str
    user_id: str
    report_type: str  # "monthly", "quarterly", "yearly", "custom"
    period_start: date
    period_end: date
    total_expenses: Decimal
    total_transactions: int
    
    # Breakdown by type
    maintenance_expenses: Decimal
    appointment_expenses: Decimal
    
    # Breakdown by vehicle
    vehicle_breakdown: List[VehicleCostSummary]
    
    # Tendencies
    compared_to_previous_period: Optional[Dict[str, float]] = None
    
    # Insights
    insights: List[str] = []  # ["Expenses increased by 15%", "More frequent oil changes"]
    
    generated_at: datetime

class PredictiveAnalytics(BaseModel):
    """Analytics predictive"""
    user_id: str
    vehicle_id: Optional[str] = None
    
    # Predictions
    predicted_monthly_cost: Decimal
    predicted_yearly_cost: Decimal
    next_maintenance_cost: Optional[Decimal] = None
    next_maintenance_date: Optional[date] = None
    
    # Recommendations
    recommendations: List[str] = []
    
    # Trust in Predictions
    confidence_score: float = Field(..., ge=0, le=1)
    
    generated_at: datetime