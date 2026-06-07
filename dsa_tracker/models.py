from datetime import UTC, date, datetime

from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


def utc_now():
    return datetime.now(UTC)


class Section(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True, nullable=False)
    description = db.Column(db.String(255), nullable=False)
    position = db.Column(db.Integer, nullable=False)
    topics = db.relationship(
        "Topic",
        backref="section",
        lazy=True,
        order_by="Topic.position",
        cascade="all, delete-orphan",
    )

    @property
    def completed_count(self):
        return sum(topic.status == "completed" for topic in self.topics)

    @property
    def progress(self):
        return round((self.completed_count / len(self.topics)) * 100) if self.topics else 0


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), unique=True, nullable=False)
    status = db.Column(db.String(20), nullable=False, default="not_started")
    position = db.Column(db.Integer, nullable=False)
    section_id = db.Column(db.Integer, db.ForeignKey("section.id"), nullable=False)
    started_at = db.Column(db.DateTime)
    completed_at = db.Column(db.DateTime)
    focus_entries = db.relationship(
        "FocusEntry", backref="topic", lazy=True, cascade="all, delete-orphan"
    )
    revisions = db.relationship(
        "Revision", backref="topic", lazy=True, cascade="all, delete-orphan"
    )

    @property
    def status_label(self):
        return self.status.replace("_", " ").title()


class FocusEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    focus_date = db.Column(db.Date, nullable=False, default=date.today, index=True)
    studied = db.Column(db.Boolean, nullable=False, default=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)

    __table_args__ = (db.UniqueConstraint("focus_date", name="one_focus_per_day"),)


class Revision(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    scheduled_for = db.Column(db.Date, nullable=False, index=True)
    completed = db.Column(db.Boolean, nullable=False, default=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=False)
    created_at = db.Column(db.DateTime(timezone=True), nullable=False, default=utc_now)
    completed_at = db.Column(db.DateTime(timezone=True))
