import os
import httpx
from fastapi import APIRouter, Request, HTTPException, Response, Depends
from typing import List, Optional
import logging
from app import schemas
from app.config import settings

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/emr",
    tags=["emr"],
    responses={404: {"description": "Not found"}},
)


async def forward_request(request: Request, method: str, path: str):
    """
    Forward request to EMR API.
    """
    emr_url = settings.EMR_API_URL
    if not emr_url:
        logger.error("EMR_API_URL not configured")
        raise HTTPException(status_code=500, detail="EMR_API_URL configuration missing")

    base_url = emr_url.rstrip("/")
    target_url = f"{base_url}/{path}"

    # Get URL query parameters
    params = dict(request.query_params)

    # Prepare headers
    headers = {
        key: value
        for key, value in request.headers.items()
        if key.lower() not in ["host", "content-length"]
    }

    try:
        body = await request.body()
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method,
                target_url,
                headers=headers,
                params=params,
                content=body,
                timeout=60.0,
            )

            # Rewrite Location header if present
            res_headers = {
                key: value
                for key, value in response.headers.items()
                if key.lower()
                not in ["content-length", "transfer-encoding", "content-encoding"]
            }

            if "location" in res_headers:
                location = res_headers["location"]
                if location.startswith(base_url):
                    # logic to rewrite location to point back to proxy
                    # We assume the path structure mirrors the proxy structure relative to /emr
                    # e.g. EMR /patients/1 -> Proxy /emr/patients/1
                    proxy_root = str(request.base_url).rstrip("/") + "/emr"
                    new_location = location.replace(base_url, proxy_root, 1)
                    res_headers["location"] = new_location

            return Response(
                content=response.content,
                status_code=response.status_code,
                headers=res_headers,
                media_type=response.headers.get("content-type"),
            )
    except httpx.RequestError as exc:
        logger.error(f"EMR proxy error to {target_url}: {exc}")
        raise HTTPException(
            status_code=502, detail=f"Failed to connect to EMR service: {str(exc)}"
        )


# --- Patients ---


@router.get("/patients/", response_model=List[schemas.Patient])
async def read_patients(request: Request, skip: int = 0, limit: int = 100):
    # We forward query params automatically in forward_request
    # But for type safety and spec documentation, we define them here.
    # Note: request.query_params will contain them.
    return await forward_request(request, "GET", "patients/")


@router.get("/patients/{patient_id}", response_model=schemas.Patient)
async def read_patient(request: Request, patient_id: int):
    return await forward_request(request, "GET", f"patients/{patient_id}")


@router.get("/patients/{patient_id}/visits", response_model=List[schemas.Visit])
async def read_patient_visits(request: Request, patient_id: int):
    return await forward_request(request, "GET", f"patients/{patient_id}/visits")


# --- Doctors ---


@router.get("/doctors/", response_model=List[schemas.Doctor])
async def read_doctors(request: Request, skip: int = 0, limit: int = 100):
    return await forward_request(request, "GET", "doctors/")


@router.get("/doctors/{doctor_id}", response_model=schemas.Doctor)
async def read_doctor(request: Request, doctor_id: int):
    return await forward_request(request, "GET", f"doctors/{doctor_id}")


# --- Visits ---


@router.get("/visits/", response_model=List[schemas.Visit])
async def read_visits(request: Request, skip: int = 0, limit: int = 100):
    return await forward_request(request, "GET", "visits/")


@router.get("/visits/{visit_id}", response_model=schemas.Visit)
async def read_visit(request: Request, visit_id: int):
    return await forward_request(request, "GET", f"visits/{visit_id}")
