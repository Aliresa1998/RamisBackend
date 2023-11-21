from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response

class CustomPagination(PageNumberPagination):
    def paginate_queryset(self, queryset, request, view=None):
        page = request.query_params.get(self.page_query_param)
        if page is None:
            return None
        
        return super().paginate_queryset(queryset, request, view)

    def get_paginated_response(self, data):
        if self.page is None:
            return Response(data)
        
        return super().get_paginated_response(data)