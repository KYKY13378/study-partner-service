"""Буквальный поиск Admin по кириллице с учетом ограничений SQLite LIKE."""
import re

from django.db.models import Q


class UnicodeSearchAdminMixin:
    def get_search_results(self, request, queryset, search_term):
        for word in search_term.split():
            condition = Q()
            for field in self.search_fields:
                condition |= Q(**{f"{field}__iregex": re.escape(word)})
            queryset = queryset.filter(condition)
        return queryset, False
