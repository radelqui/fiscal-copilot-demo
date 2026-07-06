import json
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.db import get_conn
from app.schemas import ApprovalSchema, ApprovalDecision, ApprovalListResponse

router = APIRouter(prefix="/approvals", tags=["approvals"])


@router.get("", response_model=ApprovalListResponse)
async def list_approvals(status: str | None = None, tenant_id: str | None = None):
    async with get_conn() as conn:
        conditions = []
        params: list = []
        if status:
            conditions.append("status = %s")
            params.append(status)
        if tenant_id:
            conditions.append("tenant_id = %s")
            params.append(tenant_id)

        where = f"WHERE {' AND '.join(conditions)}" if conditions else ""
        query = (
            f"SELECT id, trace_id, tenant_id, action, payload, status, "
            f"decided_by, decided_at, created_at FROM approvals {where} "
            f"ORDER BY created_at DESC"
        )
        rows = await conn.execute(query, params if params else None)
        results = await rows.fetchall()
        approvals = [
            ApprovalSchema(
                id=r[0], trace_id=r[1], tenant_id=r[2], action=r[3],
                payload=r[4] if isinstance(r[4], dict) else {},
                status=r[5], decided_by=r[6], decided_at=r[7], created_at=r[8],
            )
            for r in results
        ]
        return ApprovalListResponse(approvals=approvals, total=len(approvals))


@router.post("/{approval_id}/decide", response_model=ApprovalSchema)
async def decide_approval(approval_id: int, decision: ApprovalDecision):
    async with get_conn() as conn:
        row = await conn.execute(
            "SELECT id, status FROM approvals WHERE id = %s", [approval_id]
        )
        existing = await row.fetchone()
        if not existing:
            raise HTTPException(status_code=404, detail="Approval not found")
        if existing[1] != "pending":
            raise HTTPException(
                status_code=409,
                detail=f"Approval already decided: {existing[1]}",
            )

        now = datetime.now(timezone.utc)
        await conn.execute(
            "UPDATE approvals SET status = %s, decided_by = %s, decided_at = %s "
            "WHERE id = %s",
            [decision.decision, decision.decided_by, now, approval_id],
        )
        await conn.commit()

        row = await conn.execute(
            "SELECT id, trace_id, tenant_id, action, payload, status, "
            "decided_by, decided_at, created_at FROM approvals WHERE id = %s",
            [approval_id],
        )
        r = await row.fetchone()
        return ApprovalSchema(
            id=r[0], trace_id=r[1], tenant_id=r[2], action=r[3],
            payload=r[4] if isinstance(r[4], dict) else {},
            status=r[5], decided_by=r[6], decided_at=r[7], created_at=r[8],
        )
