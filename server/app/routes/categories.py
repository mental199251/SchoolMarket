from flask import Blueprint

from app.repositories.categories import list_categories
from app.utils.response import success_response


categories_bp = Blueprint("categories", __name__)


@categories_bp.get("")
def categories():
    return success_response(data={"items": list_categories()})
