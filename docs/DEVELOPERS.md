FastCP Developers Readme
=========================================================

Introduction
------------
FastCP manages Ubuntu servers to run PHP-based web applications.
Future support for non-PHP applications is planned. It authenticates against
existing Linux system users (no need for separate user management in the DB).

Database
--------
We use SQLite primarily to store:
  - Ownership references (e.g., which system user owns which web apps)
  - Additional metadata (e.g., database assignments for web apps)
Because user and credential management happen at the system level, the DB
does NOT store or manage user passwords.

Authentication
--------------
We rely on Python's PAM integration to authenticate existing Linux users. The
panel will:
  1. Expect the system username & password.
  2. Validate via PAM (e.g., using the `pam.py` service).
  3. Create and return a JWT upon success.

If you need to run commands as specific users, use the utility function in:
  app/utils/commands.py

Architecture
------------
- `app/main.py`: Entry point for the FastAPI application server.
- `app/services/`: Business logic.
- `app/routes/`: API endpoints or web routes for user interactions.
- `app/db/`: Database models and repositories for storing metadata in SQLite.
- `app/utils/`: Utility modules such as command execution helpers.
- `tests/`: Unit and integration tests.

Local Development
----------------
1. Make sure you have the required dependencies installed (`pip install -r requirements.txt`).
2. The application needs sufficient privileges or correct sudo configuration to authenticate system users and run commands as them.
3. Ensure you have a properly configured PAM service on your Ubuntu server.

Future Support
--------------
- Non-PHP frameworks (Python, Node.js, etc.)

Contact & Contributions
-----------------------
- Please open an issue or pull request for questions, bug reports, or feature ideas.
- Refer to LICENSE for usage and distribution terms.

