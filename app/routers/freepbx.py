from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import text
from sqlalchemy.exc import SQLAlchemyError

from app.db.freepbx import get_freepbx_db
from app.core.security import get_current_user

router = APIRouter()


@router.get("/cdr")
def listar_cdr(
    limit: int = Query(default=20, ge=1, le=100),
    current_user=Depends(get_current_user),
):
    db = get_freepbx_db()
    if db is None:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Conexión a MariaDB/FreePBX no configurada.",
        )

    try:
        rows = db.execute(
            text(
                """
                SELECT calldate, clid, src, dst, disposition, duration, billsec
                FROM cdr
                ORDER BY calldate DESC
                LIMIT :limit
                """
            ),
            {"limit": limit},
        ).mappings().all()
        return [dict(row) for row in rows]
    except SQLAlchemyError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="No se pudo consultar MariaDB/FreePBX.",
        ) from exc
    finally:
        db.close()
