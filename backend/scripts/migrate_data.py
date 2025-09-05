# scripts/migrate_data.py
# !/usr/bin/env python3
"""
Data migration utilities
"""
import asyncio
import json
import sys
from pathlib import Path

sys.path.append('.')

from app.database.session import async_session_maker
from app.models.user import User
from app.models.paper import Paper
from app.services.auth_service import auth_service
from app.services.paper_service import paper_service


async def migrate_mock_data():
    """Migrate mock data for development"""
    print("📊 Migrating mock data...")

    # Sample users
    sample_users = [
        {
            "email": "researcher@university.edu",
            "name": "Dr. Jane Researcher",
            "password": "password123",
            "affiliation": "University Research Lab",
            "research_interests": ["Machine Learning", "Natural Language Processing"]
        },
        {
            "email": "phd.student@university.edu",
            "name": "PhD Student",
            "password": "password123",
            "affiliation": "University Research Lab",
            "research_interests": ["Computer Vision", "Deep Learning"]
        }
    ]

    # Sample papers data
    sample_papers = [
        {
            "title": "Deep Learning Applications in Medical Imaging",
            "abstract": "This paper explores the applications of deep learning in medical imaging...",
            "research_area": "Medical AI",
            "target_word_count": 8000,
            "tags": ["deep learning", "medical imaging", "AI"]
        },
        {
            "title": "Natural Language Processing for Scientific Literature",
            "abstract": "We investigate NLP techniques for processing scientific papers...",
            "research_area": "NLP",
            "target_word_count": 6000,
            "tags": ["NLP", "scientific literature", "text mining"]
        }
    ]

    async with async_session_maker() as db:
        try:
            # Create users
            created_users = []
            for user_data in sample_users:
                try:
                    user = await auth_service.create_user(db=db, **user_data)
                    created_users.append(user)
                    print(f"✅ Created user: {user.email}")
                except Exception as e:
                    print(f"⚠️ User {user_data['email']} might already exist: {e}")

            # Create papers for first user
            if created_users:
                from app.schemas.paper import PaperCreate

                for paper_data in sample_papers:
                    try:
                        paper_create = PaperCreate(**paper_data)
                        paper = await paper_service.create_paper(
                            db=db,
                            user_id=created_users[0].id,
                            paper_data=paper_create
                        )
                        print(f"✅ Created paper: {paper.title}")
                    except Exception as e:
                        print(f"❌ Failed to create paper: {e}")

            print("🎉 Mock data migration completed!")

        except Exception as e:
            print(f"❌ Migration failed: {e}")


async def export_data(output_file="data_export.json"):
    """Export all data to JSON file"""
    print(f"📤 Exporting data to {output_file}...")

    async with async_session_maker() as db:
        try:
            from sqlalchemy import select

            # Export users (without passwords)
            users_result = await db.execute(select(User))
            users = users_result.scalars().all()

            # Export papers
            papers_result = await db.execute(select(Paper))
            papers = papers_result.scalars().all()

            export_data = {
                "users": [user.to_dict() for user in users],
                "papers": [paper.to_dict() for paper in papers],
                "export_date": datetime.utcnow().isoformat()
            }

            with open(output_file, 'w') as f:
                json.dump(export_data, f, indent=2, default=str)

            print(f"✅ Data exported to {output_file}")
            print(f"   Users: {len(users)}")
            print(f"   Papers: {len(papers)}")

        except Exception as e:
            print(f"❌ Export failed: {e}")


if __name__ == "__main__":
    import argparse
    from datetime import datetime

    parser = argparse.ArgumentParser(description="Data migration utilities")
    parser.add_argument("--migrate", action="store_true", help="Migrate mock data")
    parser.add_argument("--export", action="store_true", help="Export data to JSON")
    parser.add_argument("--output", default="data_export.json", help="Export output file")

    args = parser.parse_args()

    if args.migrate:
        asyncio.run(migrate_mock_data())
    elif args.export:
        asyncio.run(export_data(args.output))
    else:
        print("Please specify --migrate or --export")


