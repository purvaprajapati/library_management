from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q
from django.template.loader import render_to_string

from .models import Member
from issue_return.models import Issue
from accounts.decorators import admin_required

@admin_required
def member_list_view(request):
    members = Member.objects.all().select_related('user')
    return render(request, 'members/member_list.html', {'members': members})


@admin_required
def member_detail_view(request, pk):
    member = get_object_or_404(Member.objects.select_related('user'), pk=pk)
    member_issues = Issue.objects.filter(member=member).select_related('book')
    return render(request, 'members/member_detail.html', {
        'member': member,
        'issues': member_issues
    })


@admin_required
def edit_member_view(request, pk):
    member = get_object_or_404(Member.objects.select_related('user'), pk=pk)
    user = member.user

    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        status = request.POST.get('status', 'Active')

        if not name or not email:
            messages.error(request, "Name and Email are required.")
            return render(request, 'members/edit_member.html', {'member': member})

        user.name = name
        user.email = email
        user.phone = phone
        user.save()

        member.address = address
        member.status = status if status in ['Active', 'Inactive'] else 'Active'
        member.save()

        messages.success(request, f"Member '{user.name}' updated successfully.")
        return redirect('member_list')

    return render(request, 'members/edit_member.html', {'member': member})


@admin_required
def search_members_view(request):
    """
    AJAX Live search for members.
    Returns rendered HTML table snippet _member_table.html
    """
    query = request.GET.get('search', '').strip()
    members = Member.objects.all().select_related('user')

    if query:
        members = members.filter(
            Q(user__name__icontains=query) |
            Q(user__username__icontains=query) |
            Q(user__phone__icontains=query) |
            Q(membership_id__icontains=query)
        )

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        html = render_to_string('members/_member_table.html', {'members': members}, request=request)
        return JsonResponse({'html': html, 'count': members.count()})

    return redirect('member_list')


@admin_required
def toggle_member_status_view(request, pk):
    if request.method == 'POST' or request.headers.get('x-requested-with') == 'XMLHttpRequest':
        member = get_object_or_404(Member, pk=pk)
        member.status = 'Inactive' if member.status == 'Active' else 'Active'
        member.save()

        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'new_status': member.status,
                'message': f"Member status changed to {member.status}."
            })
        messages.success(request, f"Member status changed to {member.status}.")
        return redirect('member_list')
    return JsonResponse({'status': 'error', 'message': 'Invalid request.'}, status=400)
