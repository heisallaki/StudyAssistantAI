import argparse
import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1]))

import app.models
from app.db.session import SessionLocal
from app.models.user import User


def main() -> None:
    parser = argparse.ArgumentParser(description="Grant or revoke administrator access for a user")
    parser.add_argument("email", help="Email address of the user to update")
    parser.add_argument(
        "--revoke",
        action="store_true",
        help="Revoke administrator access instead of granting it",
    )
    args = parser.parse_args()

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.email == args.email).first()
        if user is None:
            print(f"No user found with email: {args.email}")
            sys.exit(1)

        user.is_superuser = not args.revoke
        db.commit()

        action = "revoked from" if args.revoke else "granted to"
        print(f"Administrator access {action} {args.email}")
    finally:
        db.close()


if __name__ == "__main__":
    main()