import db as db

constants = [
    db.Constant("LOWER_TAX", 7.452),
    db.Constant("FULL_TAX", 14.904),
    db.Constant("LOWER_TAX_LA_LIMIT", 43),
    db.Constant("VAT_TAX", 0.20),
    db.Constant("COST_PER_LITER", 8.2),
]

# connect to db and create session


with db.Session(db.engine) as session:
    # drop constants table
    db.Constant.__table__.drop(db.engine)
    # create constants table
    db.Constant.__table__.create(db.engine)
    # add constants to db
    session.add_all(constants)
    # commit changes
    session.commit()
    # refresh constants
    print(constants)
