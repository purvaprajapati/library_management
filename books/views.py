from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string

from .models import Book, Category
from accounts.decorators import login_required_custom, admin_required

@login_required_custom
def book_list_view(request):
    books = Book.objects.all().select_related('category')
    categories = Category.objects.all()
    user = request.user_profile

    return render(request, 'books/book_list.html', {
        'books': books,
        'categories': categories,
        'user_profile': user
    })


@login_required_custom
def book_detail_view(request, pk):
    book = get_object_or_404(Book.objects.select_related('category'), pk=pk)
    user = request.user_profile
    return render(request, 'books/book_detail.html', {
        'book': book,
        'user_profile': user
    })


@admin_required
def add_book_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        publisher = request.POST.get('publisher', '').strip()
        pub_year = request.POST.get('publication_year')
        total_copies = request.POST.get('total_copies', 1)
        image = request.FILES.get('image')

        if not title or not author or not isbn:
            messages.error(request, "Title, Author, and ISBN are required.")
            return render(request, 'books/add_book.html', {'categories': categories})

        if Book.objects.filter(isbn=isbn).exists():
            messages.error(request, "A book with this ISBN already exists.")
            return render(request, 'books/add_book.html', {'categories': categories})

        try:
            total_copies = int(total_copies)
            if total_copies < 1:
                total_copies = 1
        except ValueError:
            total_copies = 1

        try:
            pub_year = int(pub_year) if pub_year else None
        except ValueError:
            pub_year = None

        category = Category.objects.filter(id=category_id).first() if category_id else None

        book = Book.objects.create(
            title=title,
            author=author,
            isbn=isbn,
            category=category,
            description=description,
            publisher=publisher,
            publication_year=pub_year,
            total_copies=total_copies,
            available_copies=total_copies,
            image=image
        )

        messages.success(request, f"Book '{book.title}' added successfully.")
        return redirect('book_list')

    return render(request, 'books/add_book.html', {'categories': categories})


@admin_required
def edit_book_view(request, pk):
    book = get_object_or_404(Book, pk=pk)
    categories = Category.objects.all()

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        author = request.POST.get('author', '').strip()
        isbn = request.POST.get('isbn', '').strip()
        category_id = request.POST.get('category')
        description = request.POST.get('description', '').strip()
        publisher = request.POST.get('publisher', '').strip()
        pub_year = request.POST.get('publication_year')
        total_copies = request.POST.get('total_copies', 1)
        image = request.FILES.get('image')

        if not title or not author or not isbn:
            messages.error(request, "Title, Author, and ISBN are required.")
            return render(request, 'books/edit_book.html', {'book': book, 'categories': categories})

        if Book.objects.filter(isbn=isbn).exclude(pk=book.pk).exists():
            messages.error(request, "Another book with this ISBN already exists.")
            return render(request, 'books/edit_book.html', {'book': book, 'categories': categories})

        try:
            new_total = int(total_copies)
            if new_total < 1:
                new_total = 1
        except ValueError:
            new_total = book.total_copies

        # Adjust available copies dynamically based on change in total copies
        diff = new_total - book.total_copies
        new_available = max(0, book.available_copies + diff)

        book.title = title
        book.author = author
        book.isbn = isbn
        book.category = Category.objects.filter(id=category_id).first() if category_id else None
        book.description = description
        book.publisher = publisher
        book.publication_year = int(pub_year) if pub_year and pub_year.isdigit() else None
        book.total_copies = new_total
        book.available_copies = new_available

        if image:
            book.image = image

        book.save()

        messages.success(request, f"Book '{book.title}' updated successfully.")
        return redirect('book_list')

    return render(request, 'books/edit_book.html', {'book': book, 'categories': categories})


@admin_required
def delete_book_view(request, pk):
    if request.method == 'POST' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        book = get_object_or_404(Book, pk=pk)
        title = book.title
        book.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Book '{title}' deleted successfully."})
        messages.success(request, f"Book '{title}' deleted successfully.")
        return redirect('book_list')
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'}, status=400)


@login_required_custom
def search_filter_books_view(request):
    """
    AJAX Search and Filter handler for books.
    Returns rendered HTML table snippet _book_table.html
    """
    query = request.GET.get('search', '').strip()
    category_id = request.GET.get('category', '')
    availability = request.GET.get('availability', 'all')

    books = Book.objects.all().select_related('category')

    # Apply search filter
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(isbn__icontains=query) |
            Q(category__name__icontains=query)
        )

    # Apply category filter
    if category_id:
        books = books.filter(category_id=category_id)

    # Apply availability filter
    if availability == 'available':
        books = books.filter(available_copies__gt=0)
    elif availability == 'unavailable':
        books = books.filter(available_copies=0)

    user = request.user_profile

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('books/_book_table.html', {
            'books': books,
            'user_profile': user
        }, request=request)
        return JsonResponse({'html': html, 'count': books.count()})

    return redirect('book_list')


# Category Views
@admin_required
def category_list_view(request):
    categories = Category.objects.all()
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        if name:
            if Category.objects.filter(name__iexact=name).exists():
                messages.error(request, f"Category '{name}' already exists.")
            else:
                Category.objects.create(name=name)
                messages.success(request, f"Category '{name}' created successfully.")
                return redirect('category_list')
        else:
            messages.error(request, "Category name cannot be empty.")
    return render(request, 'books/category_list.html', {'categories': categories})


@admin_required
def delete_category_view(request, pk):
    if request.method == 'POST' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        category = get_object_or_404(Category, pk=pk)
        name = category.name
        category.delete()
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f"Category '{name}' deleted."})
        messages.success(request, f"Category '{name}' deleted.")
        return redirect('category_list')
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
