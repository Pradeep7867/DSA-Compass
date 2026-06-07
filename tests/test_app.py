import os
import tempfile
import unittest
from datetime import date

from dsa_tracker import create_app
from dsa_tracker.models import FocusEntry, Revision, Section, Topic, db


class TrackerTestCase(unittest.TestCase):
    def setUp(self):
        self.db_fd, self.db_path = tempfile.mkstemp(suffix=".db")
        self.app = create_app(
            {
                "TESTING": True,
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{self.db_path}",
                "SECRET_KEY": "test",
            }
        )
        self.client = self.app.test_client()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
            db.engine.dispose()
        os.close(self.db_fd)
        os.unlink(self.db_path)

    def test_curriculum_is_seeded(self):
        with self.app.app_context():
            self.assertEqual(Section.query.count(), 6)
            self.assertEqual(Topic.query.count(), 60)

    def test_dashboard_loads(self):
        pages = ["/", "/curriculum", "/focus", "/revisions"]
        for page in pages:
            with self.subTest(page=page):
                response = self.client.get(page)
                self.assertEqual(response.status_code, 200)

        dashboard = self.client.get("/")
        self.assertIn(b"Good to see you", dashboard.data)

    def test_topic_status_and_daily_focus(self):
        with self.app.app_context():
            topic_id = Topic.query.first().id

        response = self.client.post(
            f"/topics/{topic_id}/status",
            data={"status": "completed"},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)

        self.client.post("/focus", data={"topic_id": topic_id})
        with self.app.app_context():
            focus = FocusEntry.query.filter_by(focus_date=date.today()).first()
            self.assertIsNotNone(focus)

    def test_completed_topic_can_be_scheduled_for_revision(self):
        with self.app.app_context():
            topic = Topic.query.first()
            topic.status = "completed"
            db.session.commit()
            topic_id = topic.id

        response = self.client.post(
            "/revisions",
            data={"topic_id": topic_id, "scheduled_for": date.today().isoformat()},
            follow_redirects=True,
        )
        self.assertEqual(response.status_code, 200)
        with self.app.app_context():
            self.assertEqual(Revision.query.count(), 1)


if __name__ == "__main__":
    unittest.main()
