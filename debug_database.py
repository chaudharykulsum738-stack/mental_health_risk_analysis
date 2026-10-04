#!/usr/bin/env python3
"""
🔍 DEBUG SCRIPT - Check what's in your database
"""

import sqlite3
import os

DB_PATH = "data/mental_health.db"

def check_database():
    """Check if database exists and show contents"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found at: {DB_PATH}")
        print("   Run the app first to create it: streamlit run app.py")
        return
    
    print(f"\n✅ Database found at: {DB_PATH}")
    print(f"   File size: {os.path.getsize(DB_PATH)} bytes\n")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    # List all tables
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'"
    ).fetchall()
    
    print("="*70)
    print("📋 TABLES IN DATABASE:")
    print("="*70)
    for table in tables:
        print(f"  ✅ {table['name']}")
    print()
    
    # Check users table
    print("="*70)
    print("👥 USERS TABLE CONTENTS:")
    print("="*70)
    
    try:
        users = conn.execute("SELECT * FROM users").fetchall()
        
        if not users:
            print("  ❌ NO USERS FOUND!")
            print("  ℹ️  You need to create an account first")
        else:
            print(f"  Found {len(users)} user(s):\n")
            for user in users:
                print(f"  Email: {user['email']}")
                print(f"  Name: {user['name']}")
                print(f"  Password Hash: {user['password_hash'][:30]}...")
                print(f"  Salt: {user['salt'][:20]}...")
                print(f"  Created: {user['created_at']}")
                print()
    except Exception as e:
        print(f"  ❌ Error reading users: {e}")
    
    # Check login_history table
    print("="*70)
    print("🔐 LOGIN HISTORY TABLE CONTENTS:")
    print("="*70)
    
    try:
        logins = conn.execute(
            "SELECT * FROM login_history ORDER BY login_time DESC LIMIT 10"
        ).fetchall()
        
        if not logins:
            print("  ❌ NO LOGIN HISTORY FOUND")
        else:
            print(f"  Found {len(logins)} login(s):\n")
            for login in logins:
                print(f"  Email: {login['email']}")
                print(f"  Name: {login['name']}")
                print(f"  Login Time: {login['login_time']}")
                print()
    except Exception as e:
        print(f"  ❌ Error reading login history: {e}")
    
    # Check user_history table
    print("="*70)
    print("📊 USER HISTORY TABLE CONTENTS:")
    print("="*70)
    
    try:
        history = conn.execute("SELECT * FROM user_history LIMIT 5").fetchall()
        
        if not history:
            print("  ❌ NO ASSESSMENT DATA FOUND")
        else:
            print(f"  Found {len(history)} record(s):\n")
            for record in history:
                print(f"  Username: {record['username']}")
                print(f"  Date: {record['date']}")
                print(f"  Mood: {record['mood']}")
                print()
    except Exception as e:
        print(f"  ❌ Error reading user history: {e}")
    
    conn.close()
    print("="*70)

if __name__ == "__main__":
    print("\n🔍 DATABASE DEBUGGER\n")
    check_database()
