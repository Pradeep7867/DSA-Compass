from datetime import UTC, date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func

from .models import FocusEntry, Revision, Section, Topic, db


main = Blueprint("main", __name__)
VALID_STATUSES = {"not_started", "in_progress", "completed"}


@main.app_context_processor
def inject_globals():
    return {"today": date.today()}


@main.get("/")
def dashboard():
    topics = Topic.query.all()
    total_topics = len(topics)
    completed_topics = sum(topic.status == "completed" for topic in topics)
    in_progress_topics = sum(topic.status == "in_progress" for topic in topics)
    overall_progress = (
        round((completed_topics / total_topics) * 100) if total_topics else 0
    )
    today_focus = FocusEntry.query.filter_by(focus_date=date.today()).first()
    pending_revisions = (
        Revision.query.filter(
            Revision.completed.is_(False), Revision.scheduled_for <= date.today()
        )
        .order_by(Revision.scheduled_for)
        .all()
    )
    sections = Section.query.order_by(Section.position).all()

    studied_dates = {
        row[0]
        for row in db.session.query(FocusEntry.focus_date)
        .filter(FocusEntry.studied.is_(True))
        .all()
    }
    current_streak = calculate_streak(studied_dates)
    quote = get_quote(date.today().toordinal())

    return render_template(
        "dashboard.html",
        sections=sections,
        total_topics=total_topics,
        completed_topics=completed_topics,
        in_progress_topics=in_progress_topics,
        overall_progress=overall_progress,
        today_focus=today_focus,
        pending_revisions=pending_revisions,
        current_streak=current_streak,
        quote=quote,
    )


@main.get("/curriculum")
def curriculum():
    sections = Section.query.order_by(Section.position).all()
    active_section = request.args.get("section", type=int)
    return render_template(
        "curriculum.html", sections=sections, active_section=active_section
    )


@main.post("/topics/<int:topic_id>/status")
def update_topic_status(topic_id):
    topic = db.get_or_404(Topic, topic_id)
    status = request.form.get("status")
    if status not in VALID_STATUSES:
        flash("That topic status is not valid.", "danger")
        return redirect_back("main.curriculum")

    topic.status = status
    now = datetime.now(UTC)
    if status == "in_progress" and not topic.started_at:
        topic.started_at = now
    if status == "completed":
        topic.started_at = topic.started_at or now
        topic.completed_at = now
    else:
        topic.completed_at = None
    db.session.commit()
    flash(f'"{topic.title}" is now {topic.status_label}.', "success")
    return redirect_back("main.curriculum")


@main.route("/focus", methods=["GET", "POST"])
def focus():
    focus_entry = FocusEntry.query.filter_by(focus_date=date.today()).first()
    if request.method == "POST":
        topic_id = request.form.get("topic_id", type=int)
        topic = db.get_or_404(Topic, topic_id)
        if focus_entry:
            focus_entry.topic_id = topic.id
            focus_entry.studied = False
        else:
            focus_entry = FocusEntry(focus_date=date.today(), topic_id=topic.id)
            db.session.add(focus_entry)
        if topic.status == "not_started":
            topic.status = "in_progress"
            topic.started_at = datetime.now(UTC)
        db.session.commit()
        flash(f'Today’s focus is "{topic.title}".', "success")
        return redirect(url_for("main.focus"))

    topics = (
        Topic.query.filter(Topic.status != "completed")
        .join(Section)
        .order_by(Section.position, Topic.position)
        .all()
    )
    recent_entries = (
        FocusEntry.query.order_by(FocusEntry.focus_date.desc()).limit(14).all()
    )
    return render_template(
        "focus.html",
        focus_entry=focus_entry,
        topics=topics,
        recent_entries=recent_entries,
    )


@main.post("/focus/<int:entry_id>/studied")
def mark_focus_studied(entry_id):
    entry = db.get_or_404(FocusEntry, entry_id)
    entry.studied = not entry.studied
    db.session.commit()
    message = "Study session recorded." if entry.studied else "Study record removed."
    flash(message, "success")
    return redirect_back("main.focus")


@main.route("/revisions", methods=["GET", "POST"])
def revisions():
    if request.method == "POST":
        topic_id = request.form.get("topic_id", type=int)
        scheduled_for = request.form.get("scheduled_for")
        topic = db.get_or_404(Topic, topic_id)
        try:
            revision_date = date.fromisoformat(scheduled_for)
        except (TypeError, ValueError):
            flash("Choose a valid revision date.", "danger")
            return redirect(url_for("main.revisions"))

        db.session.add(Revision(topic_id=topic.id, scheduled_for=revision_date))
        db.session.commit()
        flash(f'Revision scheduled for "{topic.title}".', "success")
        return redirect(url_for("main.revisions"))

    completed_topics = (
        Topic.query.filter_by(status="completed")
        .join(Section)
        .order_by(Section.position, Topic.position)
        .all()
    )
    revision_items = Revision.query.order_by(
        Revision.completed, Revision.scheduled_for
    ).all()
    return render_template(
        "revisions.html",
        completed_topics=completed_topics,
        revision_items=revision_items,
    )


@main.post("/revisions/<int:revision_id>/complete")
def complete_revision(revision_id):
    revision = db.get_or_404(Revision, revision_id)
    revision.completed = not revision.completed
    revision.completed_at = datetime.now(UTC) if revision.completed else None
    db.session.commit()
    flash("Revision updated.", "success")
    return redirect(url_for("main.revisions"))


@main.post("/revisions/<int:revision_id>/delete")
def delete_revision(revision_id):
    revision = db.get_or_404(Revision, revision_id)
    db.session.delete(revision)
    db.session.commit()
    flash("Revision removed.", "success")
    return redirect(url_for("main.revisions"))


def redirect_back(default_endpoint):
    target = request.form.get("next")
    if target and target.startswith("/"):
        return redirect(target)
    return redirect(url_for(default_endpoint))


def calculate_streak(studied_dates):
    streak = 0
    cursor = date.today()
    while cursor in studied_dates:
        streak += 1
        cursor = date.fromordinal(cursor.toordinal() - 1)
    return streak


def get_quote(seed):
    quotes = [
        "Consistency turns difficult topics into familiar tools.",
        "A focused session is more valuable than a perfect plan.",
        "Progress in DSA is built one pattern at a time.",
        "Understand the approach, then make the code express it clearly.",
        "Small, completed sessions create serious momentum.",
    ]
    return quotes[seed % len(quotes)]
