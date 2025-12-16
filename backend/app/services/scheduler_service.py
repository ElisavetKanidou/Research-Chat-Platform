"""
Scheduler service for periodic tasks
backend/app/services/scheduler_service.py
"""
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime, timedelta
from typing import List
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import async_session_maker
from app.models.user import User
from app.models.paper import Paper
from app.services.email_service import email_service


class SchedulerService:
    """Service for scheduled tasks (reminders, reports, etc.)"""

    def __init__(self):
        self.scheduler = AsyncIOScheduler()

    def start(self):
        """Start the scheduler"""
        # Check deadlines every day at 9 AM
        self.scheduler.add_job(
            self.check_deadlines,
            CronTrigger(hour=9, minute=0),
            id='check_deadlines',
            name='Check paper deadlines and send reminders',
            replace_existing=True
        )

        # Send weekly reports every Monday at 9 AM
        self.scheduler.add_job(
            self.send_weekly_reports,
            CronTrigger(day_of_week='mon', hour=9, minute=0),
            id='weekly_reports',
            name='Send weekly progress reports',
            replace_existing=True
        )

        # Generate AI suggestions every day at 10 AM
        self.scheduler.add_job(
            self.generate_ai_suggestions,
            CronTrigger(hour=10, minute=0),
            id='ai_suggestions',
            name='Generate AI research suggestions',
            replace_existing=True
        )

        self.scheduler.start()
        print("✅ Scheduler started")

    def stop(self):
        """Stop the scheduler"""
        self.scheduler.shutdown()
        print("⏹️ Scheduler stopped")

    async def check_deadlines(self):
        """Check for upcoming deadlines and send reminders"""
        print("🔍 Checking deadlines...")

        async with async_session_maker() as db:
            try:
                # Get all papers with deadlines in the next 7 days
                seven_days_from_now = datetime.utcnow() + timedelta(days=7)
                
                # TODO: Add deadline field to Paper model
                # For now, we'll skip this
                print("⚠️ Deadline checking not fully implemented yet")

            except Exception as e:
                print(f"❌ Error checking deadlines: {str(e)}")

    async def send_weekly_reports(self):
        """Send weekly progress reports to all users"""
        print("📊 Sending weekly reports...")

        async with async_session_maker() as db:
            try:
                # Get all users who have weekly reports enabled
                result = await db.execute(select(User))
                users = result.scalars().all()

                for user in users:
                    # Check if user has weekly reports enabled
                    prefs = user.get_notification_preferences()
                    if not prefs.get('weeklyReports', False):
                        continue

                    # Get user's papers
                    papers_result = await db.execute(
                        select(Paper).where(Paper.owner_id == user.id)
                    )
                    papers = papers_result.scalars().all()

                    # Calculate stats
                    papers_worked_on = len(papers)
                    total_words = sum(paper.word_count or 0 for paper in papers)

                    # Prepare paper progress
                    paper_progress = [
                        {
                            'title': paper.title,
                            'progress': paper.progress or 0
                        }
                        for paper in papers[:5]  # Top 5 papers
                    ]

                    # Send email
                    await email_service.send_weekly_report(
                        to_email=user.email,
                        to_name=user.name,
                        papers_worked_on=papers_worked_on,
                        total_words_written=total_words,
                        comments_received=0,  # TODO: Count comments
                        upcoming_deadlines=[],  # TODO: Get deadlines
                        paper_progress=paper_progress
                    )

                    print(f"✅ Weekly report sent to {user.email}")

            except Exception as e:
                print(f"❌ Error sending weekly reports: {str(e)}")

    async def generate_ai_suggestions(self):
        """Generate AI research suggestions for users"""
        print("🤖 Generating AI suggestions...")

        async with async_session_maker() as db:
            try:
                # Get all users who have AI suggestions enabled
                result = await db.execute(select(User))
                users = result.scalars().all()

                for user in users:
                    # Check if user has AI suggestions enabled
                    prefs = user.get_notification_preferences()
                    if not prefs.get('aiSuggestions', False):
                        continue

                    # Get user's active papers
                    papers_result = await db.execute(
                        select(Paper)
                        .where(Paper.owner_id == user.id)
                        .where(Paper.status != 'completed')
                    )
                    papers = papers_result.scalars().all()

                    for paper in papers[:2]:  # Limit to 2 papers per day
                        # Generate suggestions (placeholder)
                        suggestions = [
                            "Consider adding more recent references from 2024",
                            "Your methodology section could benefit from more detail",
                            "Add statistical analysis to support your conclusions"
                        ]

                        # Send email
                        await email_service.send_ai_suggestion(
                            to_email=user.email,
                            to_name=user.name,
                            paper_title=paper.title,
                            suggestions=suggestions,
                            paper_url=f"http://localhost:3000/papers/{paper.id}"
                        )

                        print(f"✅ AI suggestions sent to {user.email} for '{paper.title}'")

            except Exception as e:
                print(f"❌ Error generating AI suggestions: {str(e)}")


scheduler_service = SchedulerService()
