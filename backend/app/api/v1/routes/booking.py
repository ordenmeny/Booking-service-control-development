from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/booking", tags=["booking"])


@router.post("/bookings")
async def create_booking() -> None:
    pass


@router.get("/bookings/{id}")
async def get_booking_by_id() -> None:
    pass


@router.get("/bookings")
async def list_bookings() -> None:
    pass


@router.delete("/bookings/{id}")
async def delete_bookings() -> None:
    pass
