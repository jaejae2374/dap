from user.core.genre.models import Genre
from user.core.genre.const import GENRE_LIST


def generate_genres() -> list[int]:
    """Generate Genres for Test."""
    genres_created = []
    for genre in GENRE_LIST:
        if not Genre.objects.filter(name=genre).exists():
            genres_created.append(
                Genre(name=genre)
            )

    Genre.objects.bulk_create(genres_created)
    return list(Genre.objects.all().values_list('id', flat=True))
