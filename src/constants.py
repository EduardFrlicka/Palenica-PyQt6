import db

LOWER_TAX = db.Constant.get("LOWER_TAX")
FULL_TAX = db.Constant.get("FULL_TAX")
LOWER_TAX_LA_LIMIT = db.Constant.get("LOWER_TAX_LA_LIMIT")
VAT_TAX = db.Constant.get("VAT_TAX")
COST_PER_LITER = db.Constant.get("COST_PER_LITER")
SERVICE_COST_PER_LA = COST_PER_LITER*2 - LOWER_TAX

DATE_FORMAT = r"%d.%m.%Y"

DILUTE_TARGETS = [0.48, 0.50, 0.52, 0.55]
