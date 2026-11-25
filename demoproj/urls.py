from django.urls import include, path

urlpatterns = [
    # Admin console removed – all management is done via the library UI
    path("", include("catalog.urls")),
    path("books/", include("books.urls")),
]

######
x
 v
urlpatterns = [
    # Admin console removed – all management is done via the library UI
    path("", include("catalog.urls")),
    path("books/", include("books.urls")),
]

 urlpatterns = [
    # Admin console removed – all management is done via the library UI
path("", include("catalog.urls")),
path("books/", include("books.urls")),
]
