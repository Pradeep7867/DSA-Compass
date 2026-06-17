from datetime import UTC, date, datetime

from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy import func
from .models import FocusEntry, Revision, Section, Topic, UserTopicProgress ,db
from .models import (
    FocusEntry,
    Revision,
    Section,
    Topic,
    User,
    db,
)
from flask_login import (
    login_user,
    logout_user,
    login_required,
    current_user,
)


main = Blueprint("main", __name__)
VALID_STATUSES = {"not_started", "in_progress", "completed"}


@main.app_context_processor
def inject_globals():
    return {"today": date.today()}

@main.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":

        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password")
        confirm_password = request.form.get("confirm_password")
        career_goal = request.form.get("career_goal")
        terms = request.form.get("terms")


        # Name Validation
        if len(name) < 3:
            flash(
                "Name must be at least 3 characters long.",
                "danger"
            )
            return redirect(url_for("main.signup"))

        # Password Match Validation
        if password != confirm_password:
            flash(
                "Passwords do not match.",
                "danger"
            )
            return redirect(url_for("main.signup"))

        # Password Length Validation
        if len(password) < 8:
            flash(
                "Password must be at least 8 characters long.",
                "danger"
            )
            return redirect(url_for("main.signup"))

        # Terms Validation
        if not terms:
            flash(
                "Please accept Terms & Conditions.",
                "danger"
            )
            return redirect(url_for("main.signup"))

        existing_user = User.query.filter_by(
            email=email
        ).first()

        if existing_user:
            flash(
                "Email already registered.",
                "danger"
            )
            return redirect(url_for("main.signup"))

        user = User(
            name=name,
            email=email,
            career_goal=career_goal
        )

        user.set_password(password)

        db.session.add(user)
        topics = Topic.query.all()
        progress_items = []

        for topic in topics:
            progress_items.append(
                UserTopicProgress(
                    user_id=user.id,
                    topic_id=topic.id,
                    status="not_started"
                )
            )

        db.session.add_all(progress_items)
        db.session.commit()
        db.session.commit()
        login_user(user)

        flash(
            "Account created successfully.",
            "success"
        )

        return redirect(url_for("main.dashboard"))

    return render_template("signup.html")
#login Route---------
@main.route("/login", methods=["GET", "POST"])
def login():

    if current_user.is_authenticated:
        return redirect(
            url_for("main.dashboard")
        )

    if request.method == "POST":

        email = request.form.get(
            "email"
        ).strip().lower()

        password = request.form.get(
            "password"
        )

        remember = bool(
            request.form.get("remember")
        )

        user = User.query.filter_by(
            email=email
        ).first()

        if not user or not user.check_password(password):

            flash(
                "Invalid email or password.",
                "danger"
            )

            return redirect(
                url_for("main.login")
            )

        login_user(
            user,
            remember=remember
        )

        flash(
            f"Welcome back, {user.name}!",
            "success"
        )

        return redirect(
            url_for("main.dashboard")
        )

    return render_template(
        "login.html"
    )

@main.get("/")
@login_required
def dashboard():

    progress_items = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()
    total_topics = Topic.query.count()

    completed_topics = sum(
        item.status == "completed"
        for item in progress_items
    )

    in_progress_topics = sum(
        item.status == "in_progress"
        for item in progress_items
    )

    overall_progress = (
        round(
            (completed_topics / total_topics) * 100
        )
        if total_topics
        else 0
    )

    today_focus = FocusEntry.query.filter_by(
        user_id=current_user.id,
        focus_date=date.today()
    ).first()

    pending_revisions = (
        Revision.query.filter(
            Revision.user_id == current_user.id,
            Revision.completed.is_(False),
            Revision.scheduled_for <= date.today()
        )
        .order_by(Revision.scheduled_for)
        .all()
    )

    sections = Section.query.order_by(
        Section.position
    ).all()

    progress_map = {
        item.topic_id: item
        for item in progress_items
    }

    section_stats = {}

    for section in sections:

        completed_count = 0

        for topic in section.topics:

            progress = progress_map.get(topic.id)

            if (
                    progress
                    and progress.status == "completed"
            ):
                completed_count += 1

        total_topics_in_section = len(
            section.topics
        )

        progress_percentage = (
            round(
                (
                        completed_count
                        / total_topics_in_section
                ) * 100
            )
            if total_topics_in_section
            else 0
        )

        section_stats[section.id] = {
            "completed": completed_count,
            "progress": progress_percentage
        }

    studied_dates = {
        row[0]
        for row in db.session.query(
            FocusEntry.focus_date
        )
        .filter(
            FocusEntry.user_id == current_user.id,
            FocusEntry.studied.is_(True)
        )
        .all()
    }

    current_streak = calculate_streak(
        studied_dates
    )

    quote = get_quote(
        date.today().toordinal()
    )

    return render_template(
        "dashboard.html",
        sections=sections,
        section_stats=section_stats,
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
@login_required
def curriculum():

    sections = Section.query.order_by(
        Section.position
    ).all()

    active_section = request.args.get(
        "section",
        type=int
    )

    progress_items = UserTopicProgress.query.filter_by(
        user_id=current_user.id
    ).all()

    progress_map = {
        item.topic_id: item
        for item in progress_items
    }
    section_stats = {}

    for section in sections:

        completed = 0

        for topic in section.topics:

            progress = progress_map.get(topic.id)

            if (
                    progress
                    and progress.status == "completed"
            ):
                completed += 1

        total = len(section.topics)

        progress_percentage = (
            round((completed / total) * 100)
            if total
            else 0
        )

        section_stats[section.id] = {
            "completed": completed,
            "progress": progress_percentage
        }

    return render_template(
        "curriculum.html",
        sections=sections,
        active_section=active_section,
        progress_map=progress_map,
        section_stats = section_stats
    )


@main.post("/topics/<int:topic_id>/status")
@login_required
def update_topic_status(topic_id):

    status = request.form.get("status")

    if status not in VALID_STATUSES:
        flash(
            "That topic status is not valid.",
            "danger"
        )
        return redirect_back(
            "main.curriculum"
        )

    progress = UserTopicProgress.query.filter_by(
        user_id=current_user.id,
        topic_id=topic_id
    ).first()

    if not progress:
        flash(
            "Progress record not found.",
            "danger"
        )
        return redirect_back(
            "main.curriculum"
        )

    progress.status = status

    now = datetime.now(UTC)

    if (
        status == "in_progress"
        and not progress.started_at
    ):
        progress.started_at = now

    if status == "completed":
        progress.started_at = (
            progress.started_at or now
        )
        progress.completed_at = now

    else:
        progress.completed_at = None

    db.session.commit()

    flash(
        "Topic status updated.",
        "success"
    )

    return redirect_back(
        "main.curriculum"
    )


@main.route("/focus", methods=["GET", "POST"])
@login_required
def focus():
    focus_entry = FocusEntry.query.filter_by(
        user_id=current_user.id,
        focus_date=date.today()
    ).first()
    if request.method == "POST":
        topic_id = request.form.get("topic_id", type=int)
        topic = db.get_or_404(Topic, topic_id)
        if focus_entry:
            focus_entry.topic_id = topic.id
            focus_entry.studied = False
        else:
            focus_entry = FocusEntry(
                user_id=current_user.id,
                focus_date=date.today(),
                topic_id=topic.id
            )
            db.session.add(focus_entry)
        progress = UserTopicProgress.query.filter_by(
            user_id=current_user.id,
            topic_id=topic.id
        ).first()
        if (
                progress
                and progress.status == "not_started"
        ):
            progress.status = "in_progress"
            progress.started_at = datetime.now(UTC)
        db.session.commit()
        flash(f'Today’s focus is "{topic.title}".', "success")
        return redirect(url_for("main.focus"))

    topics = (
        db.session.query(Topic)
        .join(
            UserTopicProgress,
            Topic.id == UserTopicProgress.topic_id
        )
        .filter(
            UserTopicProgress.user_id == current_user.id,
            UserTopicProgress.status != "completed"
        )
        .join(Section)
        .order_by(
            Section.position,
            Topic.position
        )
        .all()
    )

    recent_entries = (
        FocusEntry.query.filter_by(
            user_id=current_user.id
        )
        .order_by(
            FocusEntry.focus_date.desc()
        )
        .limit(14)
        .all()
    )
    return render_template(
        "focus.html",
        focus_entry=focus_entry,
        topics=topics,
        recent_entries=recent_entries,
    )

@main.post("/focus/<int:entry_id>/studied")
@login_required
def mark_focus_studied(entry_id):

    entry = FocusEntry.query.filter_by(
        id=entry_id,
        user_id=current_user.id
    ).first_or_404()

    entry.studied = not entry.studied

    db.session.commit()

    message = (
        "Study session recorded."
        if entry.studied
        else "Study record removed."
    )

    flash(
        message,
        "success"
    )

    return redirect_back(
        "main.focus"
    )

@main.route("/revisions", methods=["GET", "POST"])
@login_required
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

        db.session.add(Revision(  user_id=current_user.id,topic_id=topic.id, scheduled_for=revision_date))
        db.session.commit()
        flash(f'Revision scheduled for "{topic.title}".', "success")
        return redirect(url_for("main.revisions"))

    completed_topics = (
        db.session.query(Topic)
        .join(
            UserTopicProgress,
            Topic.id == UserTopicProgress.topic_id
        )
        .filter(
            UserTopicProgress.user_id == current_user.id,
            UserTopicProgress.status == "completed"
        )
        .join(Section)
        .order_by(
            Section.position,
            Topic.position
        )
        .all()
    )
    revision_items = (
        Revision.query.filter_by(
            user_id=current_user.id
        )
        .order_by(
            Revision.completed,
            Revision.scheduled_for
        )
        .all()
    )
    return render_template(
        "revisions.html",
        completed_topics=completed_topics,
        revision_items=revision_items,
    )


@main.post("/revisions/<int:revision_id>/complete")
@login_required
def complete_revision(revision_id):
    revision = Revision.query.filter_by(
        id=revision_id,
        user_id=current_user.id
    ).first_or_404()
    revision.completed = not revision.completed
    revision.completed_at = datetime.now(UTC) if revision.completed else None
    db.session.commit()
    flash("Revision updated.", "success")
    return redirect(url_for("main.revisions"))


@main.post("/revisions/<int:revision_id>/delete")
@login_required
def delete_revision(revision_id):
    revision = Revision.query.filter_by(
        id=revision_id,
        user_id=current_user.id
    ).first_or_404()
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

@main.get("/logout")
@login_required
def logout():

    logout_user()

    flash(
        "Logged out successfully.",
        "info"
    )

    return redirect(
        url_for("main.login")
    )
@main.get("/debug-progress")
def debug_progress():

    count = UserTopicProgress.query.count()

    return f"Progress Rows: {count}"