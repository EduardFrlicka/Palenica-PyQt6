from ui_py.season_edit_dialog_ui import Ui_SeasonDialog
from PyQt6 import QtWidgets, QtCore
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QDialog

import db
from sqlalchemy.orm import Session
from dialogs.alert import warning
from messages import SEASON_OVERLAP, INTERNAL_ERROR, CANNOT_DELETE_NON_EMPTY_SEASON


class SeasonDialog(QDialog, Ui_SeasonDialog):
    def __init__(self, season_id: int = None):
        super().__init__()
        self.setupUi(self)
        self.season_id = season_id

        if season_id is None:
            return

        with db.get_session() as session:
            season: db.Season = db.get_season(season_id, session)
            if season is None:
                warning(INTERNAL_ERROR)
                return

            self.dateEdit_start.setDate(QtCore.QDate(season.date_start))
            self.dateEdit_end.setDate(QtCore.QDate(season.date_end))

    def save(self):
        start = self.dateEdit_start.date().toPyDate()
        end = self.dateEdit_end.date().toPyDate()

        with db.get_session() as session:
            overlaping_season = db.get_active_season(start, self.season_id, session) or db.get_active_season(end, self.season_id, session)

            if overlaping_season:
                warning(SEASON_OVERLAP.format(overlaping_season.date_start, overlaping_season.date_end))
                return

            if self.season_id is None:
                season = db.Season(date_start=start, date_end=end)
                print("season", season)
                session.add(season)
            else:
                season: db.Season = db.get_season(self.season_id, session)
                if season is None:
                    warning(INTERNAL_ERROR)
                    return

                season.date_start = start
                season.date_end = end

            session.commit()
        self.accept()
        self.close()

    def delete(self):
        if self.season_id is None:
            self.close()
            return

        with db.get_session() as session:
            season: db.Season = db.get_season(self.season_id, session)
            if season is None:
                warning(INTERNAL_ERROR)
                return

            orders = session.query(db.Order).filter(db.Order.season_id == season.id).all()

            if orders:
                warning(CANNOT_DELETE_NON_EMPTY_SEASON)
                return

            session.delete(season)
            session.commit()
        self.accept()
        self.close()

    def set_start(self):
        if self.dateEdit_start.date() > self.dateEdit_end.date():
            self.dateEdit_end.setDate(self.dateEdit_start.date())

    def set_end(self):
        if self.dateEdit_end.date() < self.dateEdit_start.date():
            self.dateEdit_start.setDate(self.dateEdit_end.date())