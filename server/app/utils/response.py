from flask import jsonify


def success_response(data=None, message="success", status_code=200):
    return (
        jsonify(
            {
                "success": True,
                "data": data,
                "message": message,
                "error_code": None,
            }
        ),
        status_code,
    )


def error_response(error_code, message, status_code, data=None):
    return (
        jsonify(
            {
                "success": False,
                "data": data,
                "message": message,
                "error_code": error_code,
            }
        ),
        status_code,
    )

