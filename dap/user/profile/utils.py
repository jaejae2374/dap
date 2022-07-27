from dap.errors import NotAllowed
from user.profile.serializers import MentorUpdateSerializer, MenteeUpdateSerializer
from django.contrib.auth import get_user_model
User = get_user_model()

def profile_update(user: User, profile: str, data: dict) -> None:
    if profile == "mentor":
        updated_profile = user.mentor
        if not updated_profile:
            raise NotAllowed("you are not Mentor.")
        delete_academies = data.get('academy_delete', None)
        if delete_academies:
            delete_academies = list(set(delete_academies))
            existing_academies = updated_profile.academy.filter(id__in=delete_academies)
            if existing_academies.exists():
                updated_profile.academy.remove(*existing_academies)
        add_academies = data.get('academy_add', None)
        if add_academies:
            add_academies = list(set(add_academies))
            new_academies = list(set(updated_profile.academy.filter(id__in=add_academies))^set(add_academies))
            updated_profile.academy.add(*new_academies)
        mus = MentorUpdateSerializer(updated_profile, data=data, partial=True)
        mus.is_valid()
        mus.save()
    else:
        updated_profile = user.mentee
        if not updated_profile:
            raise NotAllowed("you are not Mentee.")
        mus = MenteeUpdateSerializer(updated_profile, data=data, partial=True)
        mus.is_valid()
        mus.save()

    delete_genres = data.get('genre_delete', None)
    if delete_genres:
        delete_genres = list(set(delete_genres))
        existing_genres = updated_profile.genre.filter(id__in=delete_genres)
        if existing_genres.exists():
            updated_profile.genre.remove(*existing_genres)
    add_genres = data.get('genre_add', None)
    if add_genres:
        add_genres = list(set(add_genres))
        new_genres = list(set(updated_profile.genre.filter(id__in=add_genres))^set(add_genres))
        updated_profile.genre.add(*new_genres)
    
    
    updated_profile.save()
