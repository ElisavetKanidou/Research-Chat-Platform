# scripts/create_admin.py
# !/usr/bin/env python3
"""
Create admin user script
"""
import asyncio
import sys
from getpass import getpass

# Add the app directory to Python path
sys.path.append('.')

from app.database.session import async_session_maker
from app.services.auth_service import auth_service


async def create_admin_user():
    """Create an admin user"""
    print("🔐 Creating Admin User")

    # Get user input
    email = input("Enter admin email: ")
    name = input("Enter admin name: ")
    password = getpass("Enter admin password: ")
    confirm_password = getpass("Confirm admin password: ")

    if password != confirm_password:
        print("❌ Passwords don't match")
        return

    async with async_session_maker() as db:
        try:
            # Create admin user
            admin_user = await auth_service.create_user(
                db=db,
                email=email,
                password=password,
                name=name,
                is_superuser=True
            )

            print(f"✅ Admin user created successfully!")
            print(f"   Email: {admin_user.email}")
            print(f"   ID: {admin_user.id}")

        except Exception as e:
            print(f"❌ Failed to create admin user: {e}")


if __name__ == "__main__":
    asyncio.run(create_admin_user())

