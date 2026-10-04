#!/usr/bin/env python3
"""
🔧 ACCOUNT RECOVERY SCRIPT
Shows all accounts and helps you find the right email to sign in with
""

import sqlite3
import os

DB_PATH = "data/mental_health.db"

def show_all_accounts():
    """Display all accounts in the database"""
    
    if not os.path.exists(DB_PATH):
        print(f"❌ Database not found!")
        print(f"   Location: {DB_PATH}")
        print(f"   ℹ️  Run app first: streamlit run app.py")
        return
    
    print("\n" + "="*70)
    print("🔐 YOUR ACCOUNTS")
    print("="*70 + "\n")
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    
    try:
        users = conn.execute("SELECT email, name, created_at FROM users").fetchall()
        
        if not users:
            print("❌ NO ACCOUNTS FOUND")
            print("   You need to create an account first")
            print("   1. Run: streamlit run app.py")
            print("   2. Click: 'Create Account'")
            print("   3. Fill in details")
            print("   4. Come back here to verify\n")
            return
        
        print(f"✅ Found {len(users)} account(s):\n")
        
        for i, user in enumerate(users, 1):
            print(f"Account #{i}")
            print(f"  📧 Email: {user['email']}")
            print(f"  👤 Name: {user['name']}")
            print(f"  📅 Created: {user['created_at']}")
            print()
        
        # Show login history
        print("-"*70)
        print("🔐 RECENT LOGINS:")
        print("-"*70 + "\n")
        
        logins = conn.execute(
            "SELECT email, login_time FROM login_history ORDER BY login_time DESC LIMIT 5"
        ).fetchall()
        
        if logins:
            for login in logins:
                print(f"  🔐 {login['email']} at {login['login_time']}")
        else:
            print("  ❌ No login history")
        
        print()
        
    except Exception as e:
        print(f"❌ Error: {e}")
    
    finally:
        conn.close()
    
    print("="*70)
    print("\n💡 NEXT STEPS:")
    print("   1. Copy the EMAIL from above")
    print("   2. Go to app and click 'Sign In'")
    print("   3. Paste the EMAIL")
    print("   4. Enter the PASSWORD you used when creating account")
    print("   5. Click 'Sign In'\n")

def reset_password_option():
    """Option to reset password if forgotten"""
    print("\n" + "="*70)
    print("🔓 FORGOT PASSWORD?")
    print("="*70 + "\n")
    
    if not os.path.exists(DB_PATH):
        print("❌ Database not found\n")
        return
    
    email = input("Enter the email to reset: ").strip().lower()
    if not email:
        return
    
    new_password = input("Enter new password: ").strip()
    if not new_password:
        return
    
    confirm_password = input("Confirm new password: ").strip()
    if new_password != confirm_password:
        print("❌ Passwords don't match!\n")
        return
    
    # Import hash function from app
    import hashlib
    import binascii
    
    def _hash_password(password, salt):
        """Hash password with salt using PBKDF2-SHA256"""
        return binascii.hexlify(
            hashlib.pbkdf2_hmac("sha256", password.encode(), salt.encode(), 100000)
        ).decode()
    
    try:
        conn = sqlite3.connect(DB_PATH)
        
        # Check if user exists
        user = conn.execute(
            "SELECT salt FROM users WHERE email=?", (email,)
        ).fetchone()
        
        if not user:
            print(f"❌ No account found for: {email}\n")
            conn.close()
            return
        
        # Hash new password
        new_hash = _hash_password(new_password, user[0])
        
        # Update password
        conn.execute(
            "UPDATE users SET password_hash=? WHERE email=?",
            (new_hash, email)
        )
        conn.commit()
        conn.close()
        
        print(f"\n✅ Password reset for: {email}")
        print("   Now you can sign in with your new password!\n")
        
    except Exception as e:
        print(f"❌ Error: {e}\n")

if __name__ == "__main__":
    print("\n" + "="*70)
    print("🔐 ACCOUNT RECOVERY & DEBUG")
    print("="*70)
    
    show_all_accounts()
    
    choice = input("Do you want to reset a password? (y/n): ").strip().lower()
    if choice == "y":
        reset_password_option()
