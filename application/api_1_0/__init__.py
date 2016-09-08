from flask import Blueprint

api_bluePrint = Blueprint('api', __name__)

from . import user, book, statistic, pile, pileapp, pile_charger_status, report, role_auth_check, terminal_image, \
    parameter_update
# from . import authentication, posts, users, comments, errors
