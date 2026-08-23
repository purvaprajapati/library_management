import os
import django
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from django.contrib.auth.hashers import make_password
from accounts.models import UserProfile
from books.models import Category, Book
from members.models import Member
from issue_return.models import Issue

def seed():
    print("Seeding database...")

    # 1. Create Admin
    admin_user, created = UserProfile.objects.get_or_create(
        username='admin',
        defaults={
            'name': 'System Administrator',
            'email': 'admin@library.com',
            'phone': '+91 9988776655',
            'password': make_password('admin123'),
            'role': 'admin'
        }
    )
    if created:
        print("Created Admin User (username: admin, password: admin123)")

    # 2. Create Members
    m1_user, created1 = UserProfile.objects.get_or_create(
        username='rahul',
        defaults={
            'name': 'Rahul Sharma',
            'email': 'rahul@example.com',
            'phone': '+91 9876543210',
            'password': make_password('rahul123'),
            'role': 'member'
        }
    )
    if created1:
        Member.objects.create(
            user=m1_user,
            membership_id='LIB-2026-1001',
            address='123 Tech Park, Bangalore',
            status='Active'
        )
        print("Created Member: Rahul Sharma (username: rahul, password: rahul123)")

    m2_user, created2 = UserProfile.objects.get_or_create(
        username='anita',
        defaults={
            'name': 'Anita Roy',
            'email': 'anita@example.com',
            'phone': '+91 9123456789',
            'password': make_password('anita123'),
            'role': 'member'
        }
    )
    if created2:
        Member.objects.create(
            user=m2_user,
            membership_id='LIB-2026-1002',
            address='456 Residency Road, Mumbai',
            status='Active'
        )
        print("Created Member: Anita Roy (username: anita, password: anita123)")

    # 3. Create Categories
    categories_data = [
        'Programming', 'Web Development', 'Database',
        'Artificial Intelligence', 'Mathematics', 'Fiction'
    ]
    category_objs = {}
    for cat_name in categories_data:
        cat, _ = Category.objects.get_or_create(name=cat_name)
        category_objs[cat_name] = cat
    print(f"Created/Verified {len(categories_data)} categories.")

    # 4. Create Books
    books_data = [
        {
            'title': 'Python Crash Course',
            'author': 'Eric Matthes',
            'isbn': '978-1593279288',
            'category': category_objs['Programming'],
            'publisher': 'No Starch Press',
            'publication_year': 2019,
            'total_copies': 5,
            'available_copies': 4,
            'description': 'A hands-on, project-based introduction to programming in Python.'
        },
        {
            'title': 'Learning Web Design',
            'author': 'Jennifer Robbins',
            'isbn': '978-1491960349',
            'category': category_objs['Web Development'],
            'publisher': "O'Reilly Media",
            'publication_year': 2018,
            'total_copies': 4,
            'available_copies': 3,
            'description': 'A beginner-friendly guide to HTML, CSS, JavaScript, and Web Graphics.'
        },
        {
            'title': 'Database System Concepts',
            'author': 'Abraham Silberschatz',
            'isbn': '978-0078022159',
            'category': category_objs['Database'],
            'publisher': 'McGraw-Hill',
            'publication_year': 2019,
            'total_copies': 3,
            'available_copies': 2,
            'description': 'Comprehensive foundation for database design and management.'
        },
        {
            'title': 'Artificial Intelligence: A Modern Approach',
            'author': 'Stuart Russell & Peter Norvig',
            'isbn': '978-0134610993',
            'category': category_objs['Artificial Intelligence'],
            'publisher': 'Pearson',
            'publication_year': 2020,
            'total_copies': 6,
            'available_copies': 5,
            'description': 'The standard textbook in artificial intelligence.'
        },
        {
            'title': 'Clean Code',
            'author': 'Robert C. Martin',
            'isbn': '978-0132350884',
            'category': category_objs['Programming'],
            'publisher': 'Prentice Hall',
            'publication_year': 2008,
            'total_copies': 4,
            'available_copies': 4,
            'description': 'A Handbook of Agile Software Craftsmanship.'
        }
    ]

    book_objs = []
    for b_data in books_data:
        b, _ = Book.objects.get_or_create(
            isbn=b_data['isbn'],
            defaults=b_data
        )
        book_objs.append(b)
    print(f"Created/Verified {len(books_data)} sample books.")

    # 5. Create Sample Issue Records
    rahul_member = Member.objects.get(user=m1_user)
    anita_member = Member.objects.get(user=m2_user)

    today = timezone.now().date()

    # Active issue (Normal)
    if not Issue.objects.filter(member=rahul_member, book=book_objs[0]).exists():
        Issue.objects.create(
            book=book_objs[0],
            member=rahul_member,
            due_date=today + timedelta(days=7),
            status='Issued'
        )

    # Overdue issue (3 days past due)
    if not Issue.objects.filter(member=rahul_member, book=book_objs[1]).exists():
        Issue.objects.create(
            book=book_objs[1],
            member=rahul_member,
            due_date=today - timedelta(days=3),
            status='Issued'
        )

    # Returned issue
    if not Issue.objects.filter(member=anita_member, book=book_objs[2]).exists():
        Issue.objects.create(
            book=book_objs[2],
            member=anita_member,
            due_date=today + timedelta(days=5),
            return_date=today,
            status='Returned'
        )

    print("Created sample issue transactions (active, overdue, returned).")
    print("Database seeding finished successfully!")

if __name__ == '__main__':
    seed()
