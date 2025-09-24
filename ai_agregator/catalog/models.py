from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class Category(models.Model):
    name = models.CharField(max_length=100, verbose_name="Название категории")
    slug = models.SlugField(max_length=100, unique=True, verbose_name="URL-адрес категории")
    description = models.TextField(blank=True, verbose_name="Описание категории")

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"
        ordering = ['name']

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=50, verbose_name="Название тега")
    slug = models.SlugField(max_length=50, unique=True, verbose_name="URL-адрес тега")

    class Meta:
        verbose_name = "Тег"
        verbose_name_plural = "Теги"
        ordering = ['name']

    def __str__(self):
        return self.name

from django.db.models import Avg

class AIService(models.Model):
    PRICE_MODELS = [
        ('free', 'Бесплатно'),
        ('freemium', 'Freemium'),
        ('paid', 'Платно'),
        ('subscription', 'Подписка'),
        ('credit', 'Покупка кредитов'),
    ]
    logo = models.ImageField(
        upload_to='service_logos/',
        blank=True,
        null=True,
        verbose_name="Логотип"
    )

    name = models.CharField(max_length=200, verbose_name="Название сервиса")
    slug = models.SlugField(max_length=200, unique=True, verbose_name="URL-адрес сервиса")
    short_description = models.CharField(max_length=300, verbose_name="Краткое описание")
    full_description = models.TextField(verbose_name="Полное описание")
    url = models.URLField(verbose_name="Ссылка на сервис")
    logo = models.ImageField(upload_to='service_logos/', blank=True, null=True, verbose_name="Логотип")

    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='services', verbose_name="Категория")
    tags = models.ManyToManyField(Tag, blank=True, related_name='services', verbose_name="Теги")

    price_model = models.CharField(max_length=20, choices=PRICE_MODELS, verbose_name="Модель ценообразования")
    price_description = models.CharField(max_length=200, blank=True, verbose_name="Описание цен")

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0, verbose_name="Рейтинг")
    review_count = models.PositiveIntegerField(default=0, verbose_name="Количество отзывов")

    is_verified = models.BooleanField(default=False, verbose_name="Проверенный сервис")
    is_active = models.BooleanField(default=True, verbose_name="Активный")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата обновления")

    class Meta:
        verbose_name = "AI-сервис"
        verbose_name_plural = "AI-сервисы"
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        """Возвращает средний рейтинг сервиса"""
        result = self.ratings.aggregate(Avg('score'))
        return result['score__avg'] or 0

    @property
    def rating_count(self):
        """Возвращает количество оценок сервиса"""
        return self.ratings.count()

    def get_user_rating(self, user):
        """Возвращает оценку пользователя для этого сервиса"""
        try:
            return self.ratings.get(user=user).score
        except Rating.DoesNotExist:
            return 0

from django.core.validators import MinValueValidator, MaxValueValidator

class Rating(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ratings')
    service = models.ForeignKey(AIService, on_delete=models.CASCADE, related_name='ratings')
    score = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Оценка"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Оценка"
        verbose_name_plural = "Оценки"
        unique_together = ['user', 'service']  # Один пользователь - одна оценка на сервис


    def __str__(self):
        return f"{self.user.username} - {self.service.name} - {self.score}"



class Feature(models.Model):
    service = models.ForeignKey(AIService, on_delete=models.CASCADE, related_name='features', verbose_name="Сервис")
    name = models.CharField(max_length=100, verbose_name="Название особенности")
    description = models.TextField(blank=True, verbose_name="Описание особенности")

    class Meta:
        verbose_name = "Особенность"
        verbose_name_plural = "Особенности"

    def __str__(self):
        return f"{self.name} для {self.service.name}"


class PricingPlan(models.Model):
    service = models.ForeignKey(AIService, on_delete=models.CASCADE, related_name='pricing_plans',
                                verbose_name="Сервис")
    name = models.CharField(max_length=100, verbose_name="Название тарифа")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Цена")
    currency = models.CharField(max_length=10, default='USD', verbose_name="Валюта")
    period = models.CharField(max_length=20, blank=True, verbose_name="Период (месяц/год и т.д.)")
    features = models.TextField(verbose_name="Что входит в тариф")

    class Meta:
        verbose_name = "Тарифный план"
        verbose_name_plural = "Тарифные планы"

    def __str__(self):
        return f"{self.name} для {self.service.name}"


class Bookmark(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookmarks')
    service = models.ForeignKey(AIService, on_delete=models.CASCADE, related_name='bookmarks')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата добавления")

    class Meta:
        verbose_name = "Закладка"
        verbose_name_plural = "Закладки"
        unique_together = ['user', 'service']  # Уникальная пара пользователь-сервис

    def __str__(self):
        return f"{self.user.username} - {self.service.name}"


from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import datetime


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, verbose_name="Аватар")
    bio = models.TextField(blank=True, verbose_name="О себе")
    birth_date = models.DateField(blank=True, null=True, verbose_name="Дата рождения")
    country = models.CharField(max_length=100, blank=True, verbose_name="Страна")
    city = models.CharField(max_length=100, blank=True, verbose_name="Город")
    website = models.URLField(blank=True, verbose_name="Веб-сайт")
    phone = models.CharField(max_length=20, blank=True, verbose_name="Телефон")

    class Meta:
        verbose_name = "Профиль"
        verbose_name_plural = "Профили"

    def __str__(self):
        return f"Профиль {self.user.username}"

    def age(self):
        if self.birth_date:
            today = datetime.date.today()
            return today.year - self.birth_date.year - (
                        (today.month, today.day) < (self.birth_date.month, self.birth_date.day))
        return None


# Сигналы для автоматического создания профиля при создании пользователя
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()



