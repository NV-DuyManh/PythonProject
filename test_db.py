from codegate.database.session import SessionLocal
from codegate.services.dashboard_service import dashboard_service

db = SessionLocal()
try:
    res = dashboard_service.get_pull_request_detail(db, 9, None, 1)
    print(res.json())
except Exception as e:
    import traceback
    traceback.print_exc()
