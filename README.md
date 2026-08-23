# Library Management System

A full-featured Django web application for managing library operations, including book management, member tracking, book issuing & returning, user authentication, and admin/member dashboards.

## Features

- **User Authentication & Profiles**: Registration, login, profile management, and password reset.
- **Book Management**: Add, edit, view, and categorize books.
- **Member Management**: Track active library members and view borrowing history.
- **Issue & Return System**: Issue books to members, manage returns, track overdue items, and maintain borrowing records.
- **Dashboards**: Dedicated dashboards for administrators and library members.

## Tech Stack

- **Backend**: Python, Django
- **Database**: SQLite
- **Frontend**: HTML5, CSS3, JavaScript, Django Templates

## Getting Started

### Prerequisites

- Python 3.8+
- `pip`

### Setup Instructions

1. **Clone the repository:**
   ```bash
   git clone https://github.com/purvaprajapati/library_management.git
   cd library_management
   ```

2. **Create and activate a virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install dependencies:**
   ```bash
   pip install django
   ```

4. **Run database migrations:**
   ```bash
   python manage.py migrate
   ```

5. **(Optional) Seed sample data:**
   ```bash
   python seed_data.py
   ```

6. **Start the development server:**
   ```bash
   python manage.py runserver
   ```
   Open `http://127.0.0.1:8000/` in your web browser.

## License

This project is open source and available under the [MIT License](LICENSE).
