from django.urls import path
from . import views

urlpatterns = [
    path('issue/', views.issue_book_view, name='issue_book'),
    path('issued-books/', views.issued_books_view, name='issued_books'),
    path('issue/<int:pk>/return/', views.return_book_view, name='return_book'),
    path('overdue-books/', views.overdue_books_view, name='overdue_books'),
    path('my-books/', views.my_books_view, name='my_books'),
    path('borrow/<int:book_id>/', views.member_borrow_book_view, name='member_borrow_book'),
    path('issue/borrow/<int:book_id>/', views.member_borrow_book_view, name='member_borrow_book_alt'),
]
