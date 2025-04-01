from server.app.utils.exceptions import GlobalException


ALLOWED_PERCENTAGES = {10, 20, 25, 50, 75}


def validate_persentage(percent: int) -> int:
    if percent not in ALLOWED_PERCENTAGES:
        GlobalException.CustomHTTPException.raise_exception(
            status_code=400,
            detail="Invalid percentage. Allowed: 10, 20, 25, 50, 75"
        )

    return percent
