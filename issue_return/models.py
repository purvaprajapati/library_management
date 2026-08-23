from django.db import models
from django.utils import timezone
from books.models import Book
from members.models import Member

class Issue(models.Model):
    STATUS_CHOICES = (
        ('Issued', 'Issued'),
        ('Returned', 'Returned'),
        ('Overdue', 'Overdue'),
    )

    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues')
    member = models.ForeignKey(Member, on_delete=models.CASCADE, related_name='issues')
    issue_date = models.DateField(auto_now_add=True)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Issued')

    class Meta:
        ordering = ['-issue_date']

    def __str__(self):
        return f"{self.book.title} issued to {self.member.user.name}"

    @property
    def is_overdue(self):
        if self.status == 'Returned':
            return False
        today = timezone.now().date()
        return self.due_date < today

    @property
    def days_overdue(self):
        if not self.is_overdue:
            return 0
        today = timezone.now().date()
        delta = (today - self.due_date).days
        return max(0, delta)

    @property
    def fine_amount(self):
        # Fine = Days Overdue * ₹5
        return self.days_overdue * 5
