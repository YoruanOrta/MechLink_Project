@router.get("/appointments", response_model=List[AppointmentResponse])
def get_user_appointments(
    skip: int = 0,
    limit: int = 20,
    status_filter: Optional[str] = Query(None, description="Filter by state"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get quotes from the authenticated user"""
    
    query = db.query(Appointment).filter(Appointment.user_id == current_user.id)
    
    if status_filter:
        query = query.filter(Appointment.status == status_filter)
    
    appointments = query.order_by(
        desc(Appointment.appointment_datetime)
    ).offset(skip).limit(limit).all()
    
    return appointments
