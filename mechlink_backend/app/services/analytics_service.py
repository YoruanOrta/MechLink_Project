from sqlalchemy.orm import Session
from sqlalchemy import func, text, and_, or_, desc, extract
from datetime import datetime, date, timedelta
from typing import List, Dict, Any, Optional
from decimal import Decimal
import calendar

from app.models.maintenance import MaintenanceRecord
from app.models.vehicle import Vehicle
from app.models.user import User
from app.schemas.analytics_schemas import (
    CostSummary, VehicleCostSummary, CategoryCostBreakdown,
    MonthlySpending, CostAnalyticsResponse, BudgetComparison,
    ExpenseReport, PredictiveAnalytics
)

class AnalyticsService:
    """Service for cost and expense analysis"""
    
    def __init__(self, db: Session):
        self.db = db
    
    def get_cost_summary(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> CostSummary:
        """Get user cost summary"""
        
        # Default dates: last month
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=30)
        
        try:
            # Get vehicles from the user first
            user_vehicles = self.db.query(Vehicle.id).filter(Vehicle.user_id == user_id).all()
            vehicle_ids = [v.id for v in user_vehicles]
            
            if not vehicle_ids:
                # No vehicles, return empty summary
                return CostSummary(
                    total_spent=Decimal('0'),
                    period_start=start_date,
                    period_end=end_date,
                    transaction_count=0,
                    average_per_transaction=Decimal('0')
                )
            
            # Obtain maintenance costs using user vehicles
            maintenance_costs = self.db.query(
                func.coalesce(func.sum(MaintenanceRecord.cost), 0).label('total')
            ).filter(
                and_(
                    MaintenanceRecord.vehicle_id.in_(vehicle_ids),
                    MaintenanceRecord.service_date >= start_date,
                    MaintenanceRecord.service_date <= end_date
                )
            ).scalar() or Decimal('0')
            
            # Count maintenance transactions
            maintenance_count = self.db.query(MaintenanceRecord).filter(
                and_(
                    MaintenanceRecord.vehicle_id.in_(vehicle_ids),
                    MaintenanceRecord.service_date >= start_date,
                    MaintenanceRecord.service_date <= end_date
                )
            ).count()
            
            total_spent = maintenance_costs
            transaction_count = maintenance_count
            average_per_transaction = total_spent / transaction_count if transaction_count > 0 else Decimal('0')
            
            return CostSummary(
                total_spent=total_spent,
                period_start=start_date,
                period_end=end_date,
                transaction_count=transaction_count,
                average_per_transaction=average_per_transaction
            )
            
        except Exception as e:
            print(f"Error in get_cost_summary: {e}")
            # Return empty summary on error
            return CostSummary(
                total_spent=Decimal('0'),
                period_start=start_date,
                period_end=end_date,
                transaction_count=0,
                average_per_transaction=Decimal('0')
            )
    
    def get_vehicle_cost_breakdown(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[VehicleCostSummary]:
        """Get detailed costs by vehicle"""
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)  # Last year by default
        
        try:
            vehicles = self.db.query(Vehicle).filter(Vehicle.user_id == user_id).all()
            vehicle_summaries = []
            
            for vehicle in vehicles:
                # Maintenance costs
                maintenance_cost = self.db.query(
                    func.coalesce(func.sum(MaintenanceRecord.cost), 0)
                ).filter(
                    and_(
                        MaintenanceRecord.vehicle_id == vehicle.id,
                        MaintenanceRecord.service_date >= start_date,
                        MaintenanceRecord.service_date <= end_date
                    )
                ).scalar() or Decimal('0')
                
                # Count maintenance transactions
                maintenance_count = self.db.query(MaintenanceRecord).filter(
                    and_(
                        MaintenanceRecord.vehicle_id == vehicle.id,
                        MaintenanceRecord.service_date >= start_date,
                        MaintenanceRecord.service_date <= end_date
                    )
                ).count()
                
                # Last service
                last_service = self.db.query(MaintenanceRecord).filter(
                    MaintenanceRecord.vehicle_id == vehicle.id
                ).order_by(desc(MaintenanceRecord.service_date)).first()
                
                vehicle_name = f"{vehicle.make} {vehicle.model} {vehicle.year}"
                
                vehicle_summaries.append(VehicleCostSummary(
                    vehicle_id=vehicle.id,
                    vehicle_name=vehicle_name,
                    license_plate=vehicle.license_plate,
                    total_spent=maintenance_cost,  # Just maintenance for now
                    maintenance_cost=maintenance_cost,
                    appointment_cost=Decimal('0'),  # No dating data
                    transaction_count=maintenance_count,
                    last_service_date=last_service.service_date if last_service else None
                ))
            
            return vehicle_summaries
            
        except Exception as e:
            print(f"Error in get_vehicle_cost_breakdown: {e}")
            return []
    
    def get_category_breakdown(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[CategoryCostBreakdown]:
        """Get costs by service category"""
        
        if not end_date:
            end_date = date.today()
        if not start_date:
            start_date = end_date - timedelta(days=365)
        
        try:
            # Get user vehicles
            user_vehicles = self.db.query(Vehicle.id).filter(Vehicle.user_id == user_id).all()
            vehicle_ids = [v.id for v in user_vehicles]
            
            if not vehicle_ids:
                return []
            
            # Group by type of service in maintenance
            maintenance_categories = self.db.query(
                MaintenanceRecord.service_type.label('category'),
                func.sum(MaintenanceRecord.cost).label('total_cost'),
                func.count(MaintenanceRecord.id).label('transaction_count'),
                func.max(MaintenanceRecord.service_date).label('last_service_date')
            ).filter(
                and_(
                    MaintenanceRecord.vehicle_id.in_(vehicle_ids),
                    MaintenanceRecord.service_date >= start_date,
                    MaintenanceRecord.service_date <= end_date
                )
            ).group_by(MaintenanceRecord.service_type).all()
            
            # Calculate total for percentages
            total_all_categories = sum(cat.total_cost or Decimal('0') for cat in maintenance_categories)
            
            # Convert to CategoryCostBreakdown list
            result = []
            for cat in maintenance_categories:
                total_cost = cat.total_cost or Decimal('0')
                percentage = float(total_cost / total_all_categories * 100) if total_all_categories > 0 else 0
                average_cost = total_cost / cat.transaction_count if cat.transaction_count > 0 else Decimal('0')
                
                result.append(CategoryCostBreakdown(
                    category=cat.category,
                    total_cost=total_cost,
                    transaction_count=cat.transaction_count,
                    percentage_of_total=percentage,
                    average_cost=average_cost,
                    last_service_date=cat.last_service_date
                ))
            
            # Sort by descending total cost
            return sorted(result, key=lambda x: x.total_cost, reverse=True)
            
        except Exception as e:
            print(f"Error in get_category_breakdown: {e}")
            return []
    
    def get_monthly_spending(
        self,
        user_id: str,
        months_back: int = 12
    ) -> List[MonthlySpending]:
        """Get monthly expenses"""
        
        try:
            end_date = date.today()
            start_date = end_date - timedelta(days=months_back * 30)
            
            # Get user vehicles
            user_vehicles = self.db.query(Vehicle.id).filter(Vehicle.user_id == user_id).all()
            vehicle_ids = [v.id for v in user_vehicles]
            
            if not vehicle_ids:
                return []
            
            # Maintenance per month
            maintenance_monthly = self.db.query(
                extract('year', MaintenanceRecord.service_date).label('year'),
                extract('month', MaintenanceRecord.service_date).label('month'),
                func.sum(MaintenanceRecord.cost).label('maintenance_cost'),
                func.count(MaintenanceRecord.id).label('maintenance_count')
            ).filter(
                and_(
                    MaintenanceRecord.vehicle_id.in_(vehicle_ids),
                    MaintenanceRecord.service_date >= start_date
                )
            ).group_by(
                extract('year', MaintenanceRecord.service_date),
                extract('month', MaintenanceRecord.service_date)
            ).all()
            
            # Convert to ordered list
            result = []
            monthly_data = {}
            
            for record in maintenance_monthly:
                month_key = f"{int(record.year)}-{int(record.month):02d}"
                monthly_data[month_key] = {
                    'maintenance_cost': record.maintenance_cost or Decimal('0'),
                    'maintenance_count': record.maintenance_count,
                }
            
            for month_key, data in sorted(monthly_data.items()):
                result.append(MonthlySpending(
                    month=month_key,
                    total_spent=data['maintenance_cost'],
                    maintenance_cost=data['maintenance_cost'],
                    appointment_cost=Decimal('0'),
                    transaction_count=data['maintenance_count']
                ))
            
            return result
            
        except Exception as e:
            print(f"Error in get_monthly_spending: {e}")
            return []
    
    def get_complete_analytics(
        self,
        user_id: str,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> CostAnalyticsResponse:
        """Get a complete cost analysis"""
        
        try:
            # Get all components
            period_summary = self.get_cost_summary(user_id, start_date, end_date)
            vehicles = self.get_vehicle_cost_breakdown(user_id, start_date, end_date)
            categories = self.get_category_breakdown(user_id, start_date, end_date)
            monthly_spending = self.get_monthly_spending(user_id)
            
            # Obtain user vehicles to search for the most expensive service
            user_vehicles = self.db.query(Vehicle.id).filter(Vehicle.user_id == user_id).all()
            vehicle_ids = [v.id for v in user_vehicles]
            
            most_expensive_service = None
            if vehicle_ids:
                most_expensive_maintenance = self.db.query(MaintenanceRecord).filter(
                    MaintenanceRecord.vehicle_id.in_(vehicle_ids)
                ).order_by(desc(MaintenanceRecord.cost)).first()
                
                if most_expensive_maintenance:
                    most_expensive_service = {
                        "type": "maintenance",
                        "service": most_expensive_maintenance.service_type,
                        "cost": float(most_expensive_maintenance.cost),
                        "date": most_expensive_maintenance.service_date.isoformat()
                    }
            
            # Calculate basic trends
            cost_trends = {"trend": "stable"}
            if len(monthly_spending) >= 2:
                recent_avg = sum(m.total_spent for m in monthly_spending[-3:]) / min(3, len(monthly_spending))
                older_avg = sum(m.total_spent for m in monthly_spending[:-3]) / max(1, len(monthly_spending) - 3)
                
                if recent_avg > older_avg * 1.1:
                    cost_trends["trend"] = "increasing"
                    cost_trends["change_percentage"] = float((recent_avg - older_avg) / older_avg * 100)
                elif recent_avg < older_avg * 0.9:
                    cost_trends["trend"] = "decreasing"
                    cost_trends["change_percentage"] = float((older_avg - recent_avg) / older_avg * 100)
            
            return CostAnalyticsResponse(
                user_id=user_id,
                period_summary=period_summary,
                vehicles=vehicles,
                categories=categories,
                monthly_spending=monthly_spending,
                most_expensive_service=most_expensive_service,
                cost_trends=cost_trends
            )
            
        except Exception as e:
            print(f"Error in get_complete_analytics: {e}")
            # Return empty response on error
            return CostAnalyticsResponse(
                user_id=user_id,
                period_summary=CostSummary(
                    total_spent=Decimal('0'),
                    period_start=date.today() - timedelta(days=30),
                    period_end=date.today(),
                    transaction_count=0,
                    average_per_transaction=Decimal('0')
                ),
                vehicles=[],
                categories=[],
                monthly_spending=[],
                most_expensive_service=None,
                cost_trends={"trend": "stable"}
            )