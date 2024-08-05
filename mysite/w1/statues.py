from models.models import AdviceSection, AdviceGroup, Advice
from utils.data_formatting import safe_loads, mark_advice_completed
from consts import statuesDict
from flask import g as session_data

