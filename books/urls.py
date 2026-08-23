from django.urls import path
from . import views

urlpatterns = [
    path('books/', views.book_list_view, name='book_list'),
    path('books/add/', views.add_book_view, name='add_book'),
    path('books/search/', views.search_filter_books_view, name='search_filter_books'),
    path('books/<int:pk>/', views.book_detail_view, name='book_detail'),
    path('books/<int:pk>/edit/', views.edit_book_view, name='edit_book'),
    path('books/<int:pk>/delete/', views.delete_book_view, name='delete_book'),

    # Category URLs
    path('categories/', views.category_list_view, name='category_list'),
    path('categories/<int:pk>/delete/', views.delete_category_view, name='delete_category'),
]
