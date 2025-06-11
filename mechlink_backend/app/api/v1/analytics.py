from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import datetime, date, timedelta
from typing import List, Optional
from decimal import Decimal

from app.config.database import get_db
from app.models.user import User
from app.api.deps import get_current_user
from app.services.analytics_service import AnalyticsService
from app.schemas.analytics_schemas import (
    CostSummary, VehicleCostSummary, CategoryCostBreakdown,
    MonthlySpending, CostAnalyticsResponse, BudgetComparison,
    ExpenseReport, PredictiveAnalytics
)

router = APIRouter(prefix="/analytics", tags=["analytics"])

# === COST ANALYSIS ENDPOINTS ===

@router.get("/costs/summary", response_model=CostSummary)
def get_cost_summary(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get user cost summary"""
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_cost_summary(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/costs/vehicles", response_model=List[VehicleCostSummary])
def get_vehicle_costs(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get costs broken down by vehicle"""
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_vehicle_cost_breakdown(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/costs/categories", response_model=List[CategoryCostBreakdown])
def get_category_costs(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get costs by service category"""
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_category_breakdown(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

@router.get("/costs/monthly", response_model=List[MonthlySpending])
def get_monthly_spending(
    months_back: int = Query(12, ge=1, le=24, description="Months back"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get monthly spending"""
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_monthly_spending(
        user_id=current_user.id,
        months_back=months_back
    )

@router.get("/costs/complete", response_model=CostAnalyticsResponse)
def get_complete_cost_analytics(
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get complete cost and expense analytics"""
    
    analytics_service = AnalyticsService(db)
    return analytics_service.get_complete_analytics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )

# === VEHICLE SPECIFIC ANALYTICS ===

@router.get("/costs/vehicle/{vehicle_id}", response_model=VehicleCostSummary)
def get_vehicle_specific_costs(
    vehicle_id: str,
    start_date: Optional[date] = Query(None, description="Start date (YYYY-MM-DD)"),
    end_date: Optional[date] = Query(None, description="End date (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get costs for a specific vehicle"""
    
    analytics_service = AnalyticsService(db)
    vehicles = analytics_service.get_vehicle_cost_breakdown(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Find the specific vehicle
    vehicle_data = next((v for v in vehicles if v.vehicle_id == vehicle_id), None)
    
    if not vehicle_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Vehicle not found or no cost data available"
        )
    
    return vehicle_data

# === PERIOD COMPARISONS ===

@router.get("/costs/compare/periods")
def compare_periods(
    period1_start: date = Query(..., description="Start of period 1 (YYYY-MM-DD)"),
    period1_end: date = Query(..., description="End of period 1 (YYYY-MM-DD)"),
    period2_start: date = Query(..., description="Start of period 2 (YYYY-MM-DD)"),
    period2_end: date = Query(..., description="End of period 2 (YYYY-MM-DD)"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Compare costs between two periods"""
    
    analytics_service = AnalyticsService(db)
    
    period1 = analytics_service.get_cost_summary(
        user_id=current_user.id,
        start_date=period1_start,
        end_date=period1_end
    )
    
    period2 = analytics_service.get_cost_summary(
        user_id=current_user.id,
        start_date=period2_start,
        end_date=period2_end
    )
    
    # Calculate differences
    cost_difference = period2.total_spent - period1.total_spent
    percentage_change = float(cost_difference / period1.total_spent * 100) if period1.total_spent > 0 else 0
    
    return {
        "period1": period1,
        "period2": period2,
        "comparison": {
            "cost_difference": cost_difference,
            "percentage_change": percentage_change,
            "trend": "increasing" if cost_difference > 0 else "decreasing" if cost_difference < 0 else "stable",
            "transaction_difference": period2.transaction_count - period1.transaction_count
        }
    }

# === BUDGET ANALYSIS ===

@router.get("/budget/analysis")
def get_budget_analysis(
    monthly_budget: float = Query(..., description="Monthly budget"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Specific month (1-12)"),
    year: Optional[int] = Query(None, ge=2020, le=2030, description="Specific year"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Budget analysis vs actual expenses"""
    
    # If no month/year is specified, use the current month
    if not month or not year:
        today = date.today()
        month = month or today.month
        year = year or today.year
    
    # Calculate the month's date range
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    analytics_service = AnalyticsService(db)
    month_summary = analytics_service.get_cost_summary(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Calculate remaining days in the month
    today = date.today()
    if today.year == year and today.month == month:
        days_remaining = (end_date - today).days
    else:
        days_remaining = 0
    
    # Projected monthly spending
    days_elapsed = (today - start_date).days + 1 if today >= start_date and today <= end_date else (end_date - start_date).days + 1
    projected_monthly_spend = month_summary.total_spent / days_elapsed * ((end_date - start_date).days + 1) if days_elapsed > 0 else month_summary.total_spent
    
    budget_amount = Decimal(str(monthly_budget))
    difference = budget_amount - month_summary.total_spent
    percentage_used = float(month_summary.total_spent / budget_amount * 100) if budget_amount > 0 else 0
    
    return BudgetComparison(
        budget_amount=budget_amount,
        actual_spent=month_summary.total_spent,
        difference=difference,
        percentage_used=percentage_used,
        is_over_budget=month_summary.total_spent > budget_amount,
        days_remaining=days_remaining,
        projected_monthly_spend=projected_monthly_spend
    )

# === INSIGHTS AND RECOMMENDATIONS ===

@router.get("/insights")
def get_cost_insights(
    months_back: int = Query(6, ge=3, le=12, description="Months for analysis"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get insights and recommendations on expenses"""
    
    analytics_service = AnalyticsService(db)
    
    # Retrieve data for multiple months
    monthly_data = analytics_service.get_monthly_spending(current_user.id, months_back)
    categories = analytics_service.get_category_breakdown(current_user.id)
    vehicles = analytics_service.get_vehicle_cost_breakdown(current_user.id)
    
    insights = []
    recommendations = []
    
    # Trend analysis
    if len(monthly_data) >= 3:
        recent_months = monthly_data[-3:]
        avg_recent = sum(m.total_spent for m in recent_months) / len(recent_months)
        
        older_months = monthly_data[:-3]
        if older_months:
            avg_older = sum(m.total_spent for m in older_months) / len(older_months)
            
            if avg_recent > avg_older * 1.2:
                insights.append(f"Your expenses have increased by {((avg_recent/avg_older - 1) * 100):.1f}% in the last 3 months")
                recommendations.append("Consider reviewing your maintenance habits and looking for more affordable workshops")
            elif avg_recent < avg_older * 0.8:
                insights.append(f"Your expenses have decreased by {((avg_older/avg_recent - 1) * 100):.1f}% in the last 3 months")
                recommendations.append("Great expense control! Keep it up")
    
    # Category analysis
    if categories:
        most_expensive_category = max(categories, key=lambda x: x.total_cost)
        insights.append(f"Your highest expense is in {most_expensive_category.category} (${most_expensive_category.total_cost})")
        
        if most_expensive_category.percentage_of_total > 50:
            recommendations.append(f"{most_expensive_category.category} accounts for more than 50% of your expenses. Consider looking for more affordable alternatives")
    
    # Vehicle analysis
    if len(vehicles) > 1:
        most_expensive_vehicle = max(vehicles, key=lambda x: x.total_spent)
        insights.append(f"Your most expensive vehicle is {most_expensive_vehicle.vehicle_name} (${most_expensive_vehicle.total_spent})")
        
        if most_expensive_vehicle.total_spent > sum(v.total_spent for v in vehicles) * 0.7:
            recommendations.append("One vehicle is generating the majority of your expenses. Consider evaluating if it's time for a replacement")
    
    # General recommendations
    if monthly_data:
        avg_monthly = sum(m.total_spent for m in monthly_data) / len(monthly_data)
        recommendations.append(f"Your monthly average is ${avg_monthly:.2f}. Consider setting a monthly budget")
    
    return {
        "user_id": current_user.id,
        "analysis_period": f"Last {months_back} months",
        "insights": insights,
        "recommendations": recommendations,
        "summary_stats": {
            "total_vehicles": len(vehicles),
            "total_categories": len(categories),
            "months_analyzed": len(monthly_data)
        }
    }

# === EXPORT AND REPORTS ===

@router.get("/export/monthly-report")
def export_monthly_report(
    year: int = Query(..., ge=2020, le=2030),
    month: int = Query(..., ge=1, le=12),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Export detailed monthly report"""
    
    start_date = date(year, month, 1)
    if month == 12:
        end_date = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        end_date = date(year, month + 1, 1) - timedelta(days=1)
    
    analytics_service = AnalyticsService(db)
    
    # Retrieve complete data for the month
    complete_analytics = analytics_service.get_complete_analytics(
        user_id=current_user.id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Compare with the previous month
    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    prev_start = date(prev_year, prev_month, 1)
    if prev_month == 12:
        prev_end = date(prev_year + 1, 1, 1) - timedelta(days=1)
    else:
        prev_end = date(prev_year, prev_month + 1, 1) - timedelta(days=1)
    
    prev_summary = analytics_service.get_cost_summary(
        user_id=current_user.id,
        start_date=prev_start,
        end_date=prev_end
    )
    
    # Calculate comparison
    comparison = None
    if prev_summary.total_spent > 0:
        change = complete_analytics.period_summary.total_spent - prev_summary.total_spent
        percentage_change = float(change / prev_summary.total_spent * 100)
        comparison = {
            "previous_month_total": prev_summary.total_spent,
            "change_amount": change,
            "percentage_change": percentage_change
        }
    
    return ExpenseReport(
        report_id=f"monthly-{year}-{month:02d}-{current_user.id}",
        user_id=current_user.id,
        report_type="monthly",
        period_start=start_date,
        period_end=end_date,
        total_expenses=complete_analytics.period_summary.total_spent,
        total_transactions=complete_analytics.period_summary.transaction_count,
        maintenance_expenses=sum(v.maintenance_cost for v in complete_analytics.vehicles),
        appointment_expenses=sum(v.appointment_cost for v in complete_analytics.vehicles),
        vehicle_breakdown=complete_analytics.vehicles,
        compared_to_previous_period=comparison,
        insights=[
            f"Total spent: ${complete_analytics.period_summary.total_spent}",
            f"Average per transaction: ${complete_analytics.period_summary.average_per_transaction}",
            f"Most expensive category: {complete_analytics.categories[0].category if complete_analytics.categories else 'N/A'}"
        ],
        generated_at=datetime.now()
    )