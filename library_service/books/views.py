from rest_framework import viewsets

from library_service.books.models import Book
from library_service.books.serializers import BookSerializer, BookListSerializer


class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()

    def get_serializer_class(self):
        if self.action == "list":
            return BookListSerializer
        return BookSerializer
