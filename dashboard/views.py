from django.shortcuts import render
from django.utils import timezone
from django.db.models import Count
import json

from accounts.decorators import login_required_custom
from books.models import Book, Category
from members.models import Member
from issue_return.models import Issue

@login_required_custom
def dashboard_view(request):
    user = request.user_profile
    today = timezone.now().date()

    if user.is_admin():
        # Admin Stats
        total_books = Book.objects.count()
        total_members = Member.objects.count()
        total_categories = Category.objects.count()
        
        all_issues = Issue.objects.all()
        issued_issues = all_issues.filter(status='Issued')
        returned_count = all_issues.filter(status='Returned').count()
        total_issued = issued_issues.count()
        
        available_books_count = Book.objects.filter(available_copies__gt=0).count()
        
        overdue_issues = [issue for issue in issued_issues if issue.is_overdue]
        overdue_count = len(overdue_issues)

        # Recent Data lists
        recent_issues = Issue.objects.all().select_related('book', 'member__user')[:5]
        recent_books = Book.objects.all()[:5]

        # Chart Data 1: Category Distribution
        categories = Category.objects.annotate(book_count=Count('books')).filter(book_count__gt=0)
        cat_labels = [c.name for c in categories]
        cat_counts = [c.book_count for c in categories]

        # Chart Data 2: Issue Statuses
        status_labels = ['Active Issued', 'Returned', 'Overdue']
        active_normal_issued = max(0, total_issued - overdue_count)
        status_counts = [active_normal_issued, returned_count, overdue_count]

        context = {
            'role': 'admin',
            'total_books': total_books,
            'total_members': total_members,
            'total_categories': total_categories,
            'total_issued': total_issued,
            'returned_count': returned_count,
            'available_books_count': available_books_count,
            'overdue_count': overdue_count,
            'recent_issues': recent_issues,
            'overdue_issues': overdue_issues[:5],
            'recent_books': recent_books,
            'cat_labels_json': json.dumps(cat_labels),
            'cat_counts_json': json.dumps(cat_counts),
            'status_labels_json': json.dumps(status_labels),
            'status_counts_json': json.dumps(status_counts),
        }
        return render(request, 'dashboard/admin_dashboard.html', context)

    else:
        # Member Stats
        member = getattr(user, 'member_profile', None)
        if not member:
            member = Member.objects.create(user=user, membership_id=f"LIB-MEM-{user.id}")

        all_my_issues = Issue.objects.filter(member=member).select_related('book')
        currently_issued = all_my_issues.filter(status='Issued')
        returned_issues = all_my_issues.filter(status='Returned')
        
        my_overdue = [issue for issue in currently_issued if issue.is_overdue]
        total_fine = sum(issue.fine_amount for issue in my_overdue)

        # Member Status Chart Data
        my_issued_normal = max(0, currently_issued.count() - len(my_overdue))
        member_status_labels = ['Active Books', 'Returned', 'Overdue']
        member_status_counts = [my_issued_normal, returned_issues.count(), len(my_overdue)]

        # Available Books to Borrow Discovery
        recommended_books = Book.objects.filter(available_copies__gt=0).select_related('category')[:4]

        context = {
            'role': 'member',
            'member': member,
            'my_total_count': all_my_issues.count(),
            'currently_issued_count': currently_issued.count(),
            'returned_count': returned_issues.count(),
            'overdue_count': len(my_overdue),
            'total_fine': total_fine,
            'currently_issued_list': currently_issued[:5],
            'recent_history': all_my_issues[:5],
            'recommended_books': recommended_books,
            'member_status_labels_json': json.dumps(member_status_labels),
            'member_status_counts_json': json.dumps(member_status_counts),
        }
        return render(request, 'dashboard/member_dashboard.html', context)

