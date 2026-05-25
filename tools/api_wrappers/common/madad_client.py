"""
Reusable HTTP client for the Madad Platform API.
"""
from typing import Any, Dict, List, Optional, Tuple
from pathlib import Path
import mimetypes

import httpx

from shared.config import settings


UPLOAD_MIME_TYPES_BY_EXTENSION = {
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
    ".heic": "image/heic",
    ".heif": "image/heif",
    ".tif": "image/tiff",
    ".tiff": "image/tiff",
    ".bmp": "image/bmp",
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xls": "application/vnd.ms-excel",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".csv": "text/csv",
    ".txt": "text/plain",
    ".zip": "application/zip",
}


for extension, content_type in UPLOAD_MIME_TYPES_BY_EXTENSION.items():
    mimetypes.add_type(content_type, extension)


class MadadAPIError(Exception):
    """Raised when the Madad API returns an error or cannot be reached."""

    def __init__(self, message: str, status_code: Optional[int] = None, details: Any = None):
        self.status_code = status_code
        self.details = details
        super().__init__(message)


class MadadAPIClient:
    """Small async wrapper around Madad Platform HTTP endpoints."""

    def __init__(self, base_url: Optional[str] = None, timeout: Optional[int] = None):
        resolved_base_url = base_url or settings.MADAD_API_BASE_URL
        if not resolved_base_url:
            raise ValueError("MADAD_API_BASE_URL is required")

        self.base_url = resolved_base_url.rstrip("/")
        self.timeout = timeout or settings.MADAD_API_TIMEOUT

    def _parse_response(self, response: httpx.Response) -> Dict[str, Any]:
        parsed_body: Any
        if response.content:
            try:
                parsed_body = response.json()
            except ValueError:
                parsed_body = response.text
        else:
            parsed_body = None

        if response.status_code >= 400:
            raise MadadAPIError(
                f"Madad API returned HTTP {response.status_code}",
                status_code=response.status_code,
                details=parsed_body,
            )

        result: Dict[str, Any] = {
            "status_code": response.status_code,
            "body": parsed_body,
        }

        location = response.headers.get("location")
        if location:
            result["location"] = location

        set_cookie = response.headers.get("set-cookie")
        if set_cookie:
            result["set_cookie_present"] = True

        return result

    async def request(
        self,
        method: str,
        path: str,
        *,
        json_body: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        bearer_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                response = await client.request(
                    method,
                    url,
                    json=json_body,
                    params=params,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise MadadAPIError(f"Madad API request failed: {exc}") from exc

        return self._parse_response(response)

    async def upload_file(
        self,
        path: str,
        *,
        file_path: str,
        form_data: Dict[str, Any],
        params: Optional[Dict[str, Any]] = None,
        bearer_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        local_path = Path(file_path).expanduser()
        if not local_path.is_file():
            raise MadadAPIError(f"File not found: {file_path}")

        data = {key: str(value) for key, value in form_data.items() if value is not None}
        content_type = (
            UPLOAD_MIME_TYPES_BY_EXTENSION.get(local_path.suffix.lower())
            or mimetypes.guess_type(local_path.name)[0]
            or "application/octet-stream"
        )
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                with local_path.open("rb") as file_handle:
                    response = await client.post(
                        url,
                        params=params,
                        data=data,
                        files={"file": (local_path.name, file_handle, content_type)},
                        headers=headers,
                    )
        except httpx.HTTPError as exc:
            raise MadadAPIError(f"Madad API upload failed: {exc}") from exc

        return self._parse_response(response)

    async def upload_files(
        self,
        path: str,
        *,
        file_fields: Dict[str, str],
        form_data: Optional[Dict[str, Any]] = None,
        params: Optional[Dict[str, Any]] = None,
        bearer_token: Optional[str] = None,
    ) -> Dict[str, Any]:
        headers: Dict[str, str] = {}
        if bearer_token:
            headers["Authorization"] = f"Bearer {bearer_token}"

        files: List[Tuple[str, Tuple[str, Any, str]]] = []
        opened_files: List[Any] = []
        for field_name, file_path in file_fields.items():
            local_path = Path(file_path).expanduser()
            if not local_path.is_file():
                raise MadadAPIError(f"File not found: {file_path}")

            content_type = (
                UPLOAD_MIME_TYPES_BY_EXTENSION.get(local_path.suffix.lower())
                or mimetypes.guess_type(local_path.name)[0]
                or "application/octet-stream"
            )
            file_handle = local_path.open("rb")
            opened_files.append(file_handle)
            files.append((field_name, (local_path.name, file_handle, content_type)))

        data = {key: str(value) for key, value in (form_data or {}).items() if value is not None}
        url = f"{self.base_url}{path}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=False) as client:
                response = await client.post(
                    url,
                    params=params,
                    data=data,
                    files=files,
                    headers=headers,
                )
        except httpx.HTTPError as exc:
            raise MadadAPIError(f"Madad API upload failed: {exc}") from exc
        finally:
            for file_handle in opened_files:
                file_handle.close()

        return self._parse_response(response)
