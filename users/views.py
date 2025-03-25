from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from .models import Profile
from .forms import ProfileForm

# Create your views here.

@login_required
def profile(request):
    return render(request, 'users/profile.html', {
        'profile': request.user.profile,
    })

@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user.profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль успешно обновлен.')
            return redirect('users:profile')
    else:
        form = ProfileForm(instance=request.user.profile)
    
    return render(request, 'users/profile_edit.html', {
        'form': form,
    })

@login_required
def favorites(request):
    # TODO: Implement favorites functionality
    return render(request, 'users/favorites.html')

@login_required
def view_history(request):
    # TODO: Implement view history functionality
    return render(request, 'users/view_history.html')
