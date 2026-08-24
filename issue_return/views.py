from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta

from .models import Issue
from books.models import Book
from members.models import Member
from accounts.decorators import login_required_custom, admin_required, member_required

@admin_required
def issue_book_view(request):
    members = Member.objects.filter(status='Active').select_related('user')
    books = Book.objects.filter(available_copies__gt=0)
    preselected_book_id = request.GET.get('book_id')

    if request.method == 'POST':
        member_id = request.POST.get('member_id')
        book_id = request.POST.get('book_id')
        due_date_str = request.POST.get('due_date')

        if not member_id or not book_id or not due_date_str:
            messages.error(request, "Please select member, book, and due date.")
            return render(request, 'issue_return/issue_book.html', {
                'members': members,
                'books': books,
                'preselected_book_id': preselected_book_id
            })

        member = get_object_or_404(Member, id=member_id)
        book = get_object_or_404(Book, id=book_id)

        # Rule 1: Stock check
        if book.available_copies <= 0:
            messages.error(request, f"Cannot issue '{book.title}'. No copies available.")
            return redirect('issue_book')

        # Rule 2: Prevent duplicate active issue for same member & book
        if Issue.objects.filter(member=member, book=book, status='Issued').exists():
            messages.error(request, f"This book '{book.title}' is already issued to member {member.user.name}.")
            return redirect('issue_book')

        try:
            due_date = datetime.strptime(due_date_str, '%Y-%m-%d').date()
        except ValueError:
            due_date = timezone.now().date() + timedelta(days=7)

        # Create Issue record
        issue = Issue.objects.create(
            book=book,
            member=member,
            due_date=due_date,
            status='Issued'
        )

        # Decrement available copies
        book.available_copies -= 1
        book.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Book '{book.title}' issued successfully to {member.user.name}."})

        messages.success(request, f"Book '{book.title}' issued successfully to {member.user.name}.")
        return redirect('issued_books')

    # Default due date = 7 days from today
    default_due_date = (timezone.now() + timedelta(days=7)).strftime('%Y-%m-%d')

    return render(request, 'issue_return/issue_book.html', {
        'members': members,
        'books': books,
        'preselected_book_id': preselected_book_id,
        'default_due_date': default_due_date
    })


@admin_required
def return_book_view(request, pk):
    """
    AJAX Return Book handler.
    Updates issue status to 'Returned', sets return_date, increments available copies.
    """
    if request.method == 'POST' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        issue = get_object_or_404(Issue.objects.select_related('book', 'member__user'), pk=pk)

        if issue.status == 'Returned':
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': 'This book is already returned.'})
            messages.warning(request, 'This book is already returned.')
            return redirect('issued_books')

        # Perform return operations
        issue.return_date = timezone.now().date()
        issue.status = 'Returned'
        issue.save()

        # Increment book available copies
        book = issue.book
        book.available_copies += 1
        book.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'message': f"Book '{book.title}' returned successfully.",
                'return_date': issue.return_date.strftime('%d %b %Y'),
                'available_copies': book.available_copies
            })

        messages.success(request, f"Book '{book.title}' returned successfully.")
        return redirect('issued_books')

    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@login_required_custom
def issued_books_view(request):
    user = request.user_profile
    if user.is_admin():
        issues = Issue.objects.all().select_related('book', 'member__user')
    else:
        member = getattr(user, 'member_profile', None)
        issues = Issue.objects.filter(member=member).select_related('book', 'member__user')

    return render(request, 'issue_return/issued_books.html', {'issues': issues, 'user_profile': user})


@admin_required
def overdue_books_view(request):
    today = timezone.now().date()
    # Filter issued books with due_date < today
    all_issued = Issue.objects.filter(status='Issued').select_related('book', 'member__user')
    overdue_issues = [issue for issue in all_issued if issue.is_overdue]

    return render(request, 'issue_return/overdue_books.html', {
        'overdue_issues': overdue_issues,
        'today': today
    })


@member_required
def my_books_view(request):
    user = request.user_profile
    member = getattr(user, 'member_profile', None)
    if not member:
        member = Member.objects.create(user=user, membership_id=f"LIB-MEM-{user.id}")

    currently_issued = Issue.objects.filter(member=member, status='Issued').select_related('book')
    returned_books = Issue.objects.filter(member=member, status='Returned').select_related('book')

    return render(request, 'issue_return/my_books.html', {
        'currently_issued': currently_issued,
        'returned_books': returned_books,
        'member': member
    })


@member_required
def member_borrow_book_view(request, book_id):
    """
    Allows a logged-in member to borrow/issue an available book directly.
    """
    user = request.user_profile
    member = getattr(user, 'member_profile', None)
    if not member:
        member = Member.objects.create(user=user, membership_id=f"LIB-MEM-{user.id}")

    book = get_object_or_404(Book, pk=book_id)

    # Validation checks
    if book.available_copies <= 0:
        msg = f"Sorry, '{book.title}' is currently out of stock."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': msg})
        messages.error(request, msg)
        return redirect('book_list')

    if Issue.objects.filter(member=member, book=book, status='Issued').exists():
        msg = f"You already have an active issue for '{book.title}'."
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': msg})
        messages.warning(request, msg)
        return redirect('my_books')

    # Default borrow period for member self-service: 14 days
    due_date = timezone.now().date() + timedelta(days=14)

    Issue.objects.create(
        book=book,
        member=member,
        due_date=due_date,
        status='Issued'
    )

    book.available_copies -= 1
    book.save()

    msg = f"Successfully borrowed '{book.title}'! Due date: {due_date.strftime('%d %b %Y')}."
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'status': 'success',
            'message': msg,
            'available_copies': book.available_copies,
            'due_date': due_date.strftime('%d %b %Y')
        })

    messages.success(request, msg)
    return redirect('my_books')

