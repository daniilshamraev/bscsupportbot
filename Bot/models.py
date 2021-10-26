from django.db import models


class Appl(models.Model):
    DateStart = models.DateTimeField(
        verbose_name='Дата создания', auto_now=True
    )
    DateStop = models.DateTimeField(
        verbose_name='Дата закрытия', null=True, blank=True
    )
    employee_close = models.CharField(
        verbose_name='Сотрудник закрывший заявку', max_length=20, null=True, blank=True
    )
    Ship = models.CharField(
        verbose_name='Название лодки', max_length=40, null=True, blank=True
    )
    Active = models.BooleanField(
        verbose_name='Активна', default=True
    )
    type = models.IntegerField(
        verbose_name='Кому заявка', choices=
        [
            (1, 'Техники'),
            (2, 'ШКИПЕРЫ'),
            (3, 'ОСТАВИТЬ ОТЗЫВ'),
        ]
    )

    def __str__(self):
        return f'Заявка №{self.id}'

    class Meta:
        verbose_name = 'Заявка'
        verbose_name_plural = 'Заявки'


class Message(models.Model):
    text = models.TextField(
        verbose_name='Текст сообщения', null=True, blank=True
    )
    metadata = models.JSONField(
        verbose_name='Метаданные', null=True, blank=True
    )
    time = models.DateTimeField(
        verbose_name='Время отправки', auto_now=True
    )
    app = models.ForeignKey(
        Appl, verbose_name='Заявка', null=True, blank=True, on_delete=models.CASCADE
    )

    def __str__(self):
        return f'Сообщение №{self.id} от {self.time}'

    class Meta:
        verbose_name = 'Сообщение'
        verbose_name_plural = 'Сообщения'


class Client(models.Model):
    id = models.IntegerField(
        verbose_name='ID Telegram', primary_key=True
    )
    telegram_username = models.CharField(
        verbose_name='Клиент', max_length=20
    )
    app = models.ForeignKey(
        Appl, on_delete=models.CASCADE, verbose_name='Заявки клиента', null=True
    )
    chat_id = models.CharField(
        verbose_name='id чата', max_length=20
    )

    def __str__(self):
        return f'Клиент {self.telegram_username}'

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'
