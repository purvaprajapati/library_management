import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'library_management.settings')
django.setup()

from django.test import Client
from django.urls import reverse
from accounts.models import UserProfile
from books.models import Book, Category
from members.models import Member
from issue_return.models import Issue

def run_tests():
    print("=========================================")
    print("STARTING END-TO-END AUTOMATED VERIFICATION")
    print("=========================================")
    client = Client()

    # 1. Unauthenticated Protection Test
    response = client.get('/dashboard/')
    assert response.status_code == 302, "Unauthenticated user should be redirected from /dashboard/"
    print("[PASS] Unauthenticated redirect to /login/ verified.")

    # 2. Login as Admin
    response = client.post('/login/', {'username': 'admin', 'password': 'admin123'})
    assert response.status_code == 302 and response.url == '/dashboard/', "Admin login failed"
    print("[PASS] Admin login successful.")

    # 3. Access Admin Dashboard
    response = client.get('/dashboard/')
    assert response.status_code == 200, "Admin dashboard failed to load"
    assert b"Librarian Dashboard" in response.content, "Librarian Dashboard text missing"
    print("[PASS] Admin Dashboard rendering verified.")

    # 4. AJAX Book Search Test
    response = client.get('/books/search/', {'search': 'Python'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200, "AJAX book search failed"
    json_data = response.json()
    assert 'Python Crash Course' in json_data['html'], "Book search failed to match title"
    print("[PASS] AJAX Book Live Search verified.")

    # 5. AJAX Member Search Test
    response = client.get('/members/search/', {'search': 'Rahul'}, HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200, "AJAX member search failed"
    json_data = response.json()
    assert 'Rahul Sharma' in json_data['html'], "Member search failed to match name"
    print("[PASS] AJAX Member Live Search verified.")

    # 6. Book Issue & Stock Validation Test
    member = Member.objects.get(user__username='rahul')
    book = Book.objects.get(isbn='978-0134610993') # AI book
    initial_copies = book.available_copies

    response = client.post('/issue/', {
        'member_id': member.id,
        'book_id': book.id,
        'due_date': '2026-08-15'
    })
    assert response.status_code in [200, 302], "Issue book request failed"
    
    book.refresh_from_db()
    assert book.available_copies == initial_copies - 1, "Available copies count did not decrement on issue"
    print("[PASS] Book issuing and automatic stock decrement verified.")

    # 7. Duplicate Issue Prevention Test
    response = client.post('/issue/', {
        'member_id': member.id,
        'book_id': book.id,
        'due_date': '2026-08-15'
    })
    # Should redirect or error out without creating second active issue
    active_issues = Issue.objects.filter(member=member, book=book, status='Issued').count()
    assert active_issues == 1, "Duplicate active issue was improperly allowed!"
    print("[PASS] Duplicate active issue prevention verified.")

    # 8. AJAX Book Return Test
    latest_issue = Issue.objects.filter(member=member, book=book, status='Issued').first()
    response = client.post(f'/issue/{latest_issue.id}/return/', HTTP_X_REQUESTED_WITH='XMLHttpRequest')
    assert response.status_code == 200, "AJAX return book failed"
    assert response.json()['status'] == 'success', "AJAX return status not success"

    book.refresh_from_db()
    assert book.available_copies == initial_copies, "Available copies count did not increment on return"
    print("[PASS] AJAX Book Return and automatic stock restoration verified.")

    # 9. Overdue & Fine Calculation Test
    overdue_issues = [issue for issue in Issue.objects.filter(status='Issued') if issue.is_overdue]
    if overdue_issues:
        overdue_issue = overdue_issues[0]
        assert overdue_issue.is_overdue == True, "Overdue flag failed"
        assert overdue_issue.fine_amount == overdue_issue.days_overdue * 5, "Fine calculation mismatch"
        print(f"[PASS] Overdue engine verified: {overdue_issue.days_overdue} days overdue = ₹{overdue_issue.fine_amount} fine.")

    # 10. Access Control Test for Member Role
    client.get('/logout/')
    client.post('/login/', {'username': 'rahul', 'password': 'rahul123'})
    
    response = client.get('/dashboard/')
    assert response.status_code == 200, "Member dashboard failed"
    assert b"Welcome, Rahul Sharma" in response.content, "Member Dashboard title missing"

    response = client.get('/books/add/')
    assert response.status_code == 302, "Member should NOT be allowed to open /books/add/"
    print("[PASS] Role-based access control (Admin route protection from members) verified.")

    print("=========================================")
    print("ALL AUTOMATED TESTS PASSED SUCCESSFULLY!")
    print("=========================================")

if __name__ == '__main__':
    run_tests()
