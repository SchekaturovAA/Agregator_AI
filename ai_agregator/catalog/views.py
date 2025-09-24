from django.shortcuts import render

from .models import AIService

from django.db.models import Prefetch, Avg, Count
from .models import Category, AIService, Bookmark, Rating


def home(request):
    # Оптимизированный запрос с аннотацией среднего рейтинга
    categories = Category.objects.prefetch_related(
        Prefetch('services',
                 queryset=AIService.objects.annotate(
                     avg_rating_annotated=Avg('ratings__score'),
                     rating_count_annotated=Count('ratings')
                 )
                 )
    ).all()

    user_bookmarks = []
    user_ratings = {}

    if request.user.is_authenticated:
        user_bookmarks = Bookmark.objects.filter(user=request.user).values_list('service_id', flat=True)
        # Получаем оценки пользователя
        user_ratings_query = Rating.objects.filter(user=request.user).values_list('service_id', 'score')
        # Преобразуем в словарь
        user_ratings = {service_id: score for service_id, score in user_ratings_query}

    return render(request, 'home.html', {
        'categories': categories,
        'user_bookmarks': user_bookmarks,
        'user_ratings': user_ratings
    })


from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.contrib import messages
from .forms import CustomUserCreationForm  # Импортируем нашу кастомную форму


def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно!')
            return redirect('home')
        else:
            messages.error(request, 'Ошибка регистрации. Проверьте введенные данные.')
    else:
        form = CustomUserCreationForm()

    return render(request, 'registration/register.html', {'form': form})

from django.contrib.auth import logout
from django.contrib import messages
from django.shortcuts import redirect

def custom_logout(request):
    logout(request)
    messages.info(request, "Вы успешно вышли из системы.")
    return redirect('login')


from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Bookmark

@login_required
def profile(request):
    # Получаем или создаем профиль для пользователя, если его нет
    try:
        profile = request.user.profile
    except Profile.DoesNotExist:
        profile = Profile.objects.create(user=request.user)

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Ваш профиль был успешно обновлен!')
            return redirect('profile')
        else:
            messages.error(request, 'Пожалуйста, исправьте ошибки в форме.')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }

    return render(request, 'profile.html', context)



@login_required
def toggle_bookmark(request, service_id):
    service = get_object_or_404(AIService, id=service_id)

    # Проверяем, существует ли уже закладка
    bookmark_exists = Bookmark.objects.filter(user=request.user, service=service).exists()

    if bookmark_exists:
        # Удаляем закладку, если она существует
        Bookmark.objects.filter(user=request.user, service=service).delete()
        return JsonResponse({'status': 'removed', 'message': 'Закладка удалена'})
    else:
        # Создаем новую закладку
        Bookmark.objects.create(user=request.user, service=service)
        return JsonResponse({'status': 'added', 'message': 'Добавлено в закладки'})

@login_required
def bookmarks_list(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('service')
    return render(request, 'bookmarks.html', {'bookmarks': bookmarks})


from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Rating


@require_POST
@login_required
def rate_service(request, service_id):
    service = get_object_or_404(AIService, id=service_id)
    score = request.POST.get('score')

    try:
        score = int(score)
        if score < 1 or score > 5:
            raise ValueError
    except (ValueError, TypeError):
        return JsonResponse({'error': 'Некорректная оценка'}, status=400)

    # Создаем или обновляем оценку
    rating, created = Rating.objects.update_or_create(
        user=request.user,
        service=service,
        defaults={'score': score}
    )

    # Пересчитываем средний рейтинг
    from django.db.models import Avg
    average_rating = service.ratings.aggregate(Avg('score'))['score__avg'] or 0

    return JsonResponse({
        'status': 'success',
        'average_rating': round(average_rating, 1),
        'rating_count': service.ratings.count(),
        'user_rating': score
    })



