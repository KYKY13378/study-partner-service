"""Проверка параметров поиска. Изменение данных через веб-формы — следующий этап."""
from django import forms

from requests.queries import SORT_FIELDS


class RequestFiltersForm(forms.Form):
    q = forms.CharField(label="Поиск", max_length=100, required=False)
    date = forms.DateField(label="Дата занятия", required=False, input_formats=["%Y-%m-%d"],
                           error_messages={"invalid": "Укажите дату в формате ГГГГ-ММ-ДД."})
    subject = forms.IntegerField(label="Предмет", required=False, min_value=1, max_value=2147483647)
    user = forms.IntegerField(label="Автор", required=False, min_value=1, max_value=2147483647)
    format = forms.ChoiceField(label="Формат", required=False,
                               choices=[("", "Все"), ("онлайн", "Онлайн"), ("офлайн", "Офлайн")])
    status = forms.ChoiceField(label="Статус", choices=[
        ("all", "Все"), ("active", "Активные"), ("closed", "Закрытые"),
    ])
    sort = forms.CharField(label="Сортировка", max_length=50, required=False)
    per_page = forms.TypedChoiceField(label="Запросов на странице", required=False, coerce=int,
                                      choices=[(n, n) for n in (2, 5, 10, 20)])
    view = forms.ChoiceField(label="Вид", choices=[("cards", "Карточки"), ("table", "Таблица")])

    def clean_date(self):
        day = self.cleaned_data["date"]
        if day and self.data.get("date") != day.isoformat():
            raise forms.ValidationError("Укажите дату в формате ГГГГ-ММ-ДД.")
        return day

    def clean_sort(self):
        value = self.cleaned_data["sort"]
        return value if value in SORT_FIELDS else "date"
