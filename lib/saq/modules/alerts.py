# vim: sw=4:ts=4:et

import fcntl
import gc
import json
import logging
import os
import os.path
import saq

import saq
import saq.database

from saq.analysis import Analysis, Observable
from saq.constants import *
from saq.database import get_db_connection, use_db, ALERT, DatabaseSession
from saq.error import report_exception
from saq.modules import AnalysisModule

from sqlalchemy.orm.exc import NoResultFound

# DEPRECATED
class ACEAlertsAnalysis(Analysis):
    """What other alerts have we seen this in?"""

    def initialize_details(self):
        self.details = []

    @property
    def jinja_template_path(self):
        return "analysis/related_alerts.html"

    def generate_summary(self):
        if self.details:
            return "Related Alerts Analysis ({0} alerts)".format(len(self.details))
        return None

class ACEAlertDispositionAnalyzer(AnalysisModule):
    """Cancels any further analysis if the disposition has been set by the analyst."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_mode = self.config['target_mode']

    def execute_pre_analysis(self):
        self.check_disposition()

    def execute_threaded(self):
        self.check_disposition()

    @use_db
    def check_disposition(self, db, c):
        c.execute("SELECT disposition FROM alerts WHERE uuid = %s", (self.root.uuid,))
        row = c.fetchone()
        # did the alert vanish from the database?
        if row is None:
            logging.warning("alert {} seems to have vanished from the database".format(self.root.uuid))
            self.engine.cancel_analysis()

        disposition = row[0]
        if disposition is not None:
            logging.info("alert {} has been dispositioned - canceling analysis".format(self.root.uuid))
            self.engine.cancel_analysis()

class ACEDetectionAnalyzer(AnalysisModule):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.target_mode = self.config['target_mode']

    def execute_post_analysis(self):
        # do not alert on a root that has been whitelisted
        if not saq.FORCED_ALERTS and self.root.whitelisted:
            logging.debug("{} has been whitelisted".format(self.root))
            return True

        if saq.FORCED_ALERTS or self.root.has_detections():
            logging.info("{} has {} detection points - changing mode to {}".format(
                         self.root, len(self.root.all_detection_points), self.target_mode))
            self.root.analysis_mode = self.target_mode

        return True
