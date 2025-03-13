from flask import Blueprint, jsonify
from ..db import get_db

sectors_bp = Blueprint('sectors', __name__)

@sectors_bp.route('/sectors', methods=['GET'])
def get_sectors():
    # TODO: Implement after database tests show what's needed
    pass

@sectors_bp.route('/sectors/<sector>/metrics', methods=['GET'])
def get_sector_metrics(sector):
    # TODO: Implement after database tests show what's needed
    pass
