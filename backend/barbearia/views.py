from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required

@staff_member_required
def dashboard_barbeiro(request):
    return render(request, 'dashboard.html')