from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from faker import Faker
from user.profile.tests import MentorFactory, MenteeFactory
from user.core.genre.utils import generate_genres
from util.location.tests import LocationFactory
from user.core.academy.tests import AcademyFactory
from user.core.genre.models import Genre
from lesson.lesson.models import Lesson
from datetime import datetime, timedelta
from user.tests import UserFactory
import pytz 

User = get_user_model()

class LessonFactory(DjangoModelFactory):
    class Meta:
        model = Lesson

    @classmethod
    def create(cls, **kwargs) -> Lesson:
        fake = Faker("ko_KR")
        fake_started_at = fake.date_time_this_month(after_now=True)
        fake_finished_at = fake_started_at + timedelta(hours=2)
        lesson = Lesson.objects.create(
            title=kwargs.get("title", fake.sentence()),
            description=kwargs.get("description", fake.sentence()),
            started_at=kwargs.get("started_at", fake_started_at),
            finished_at=kwargs.get("finished_at", fake_finished_at),
            academy=kwargs.get("academy", AcademyFactory.create()),
            price=kwargs.get("price", fake.random_choices(elements=range(10000, 30000, 1000), length=1)[0]),
            recruit_number=kwargs.get("recruit_number", fake.random_choices(elements=range(5, 30), length=1)[0]),
            location=kwargs.get("location", LocationFactory.create(type="academy")),
            genre=kwargs.get("genre", Genre.objects.get(id=fake.random_choices(elements=range(1, 11), length=1)[0])),
        )
        if kwargs.get('mentor'):
            lesson.mentor.set(kwargs.get('mentor'))
        if kwargs.get('mentee'):
            lesson.mentee.set(kwargs.get('mentee'))
        return lesson

        
class LessonTestCase(TestCase):
    """
    # Test Lesson APIs.
        [POST] /lesson
        []
        []
        []
        []
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.genres_id = generate_genres()
        # TODO: use bulk_create?
        cls.mentors = []
        for i in range(3):
            cls.mentors.append(
                UserFactory.create(mentor=MentorFactory.create())
            )
        cls.mentors_tokens = ["Token " + str(mentor.auth_token) for mentor in cls.mentors]
        cls.mentees = []
        for i in range(5):
            cls.mentees.append(
                UserFactory.create(mentee=MenteeFactory.create())
            )
        cls.mentees_tokens = ["Token " + str(mentee.auth_token) for mentee in cls.mentees]
        cls.academy_location = LocationFactory.create(
            type="academy",
            detail="서울시 강남구 언주로 107",
            city="서울시",
            district="강남구",
            description="테스트 학원 위치입니다."
        )
        cls.academy = AcademyFactory.create(
            name="사자후",
            email="sazahoo@test.com",
            contact="01025911955",
            description="테스트 학원 입니다.",
            location=cls.academy_location
        )
        cls.lesson_location_data = {
            'detail': "서울시 강남구 언주로 107",
            'city': "서울시",
            'district': "강남구",
            'description': "테스트 수업 위치입니다."
        }
        cls.lesson_location = LocationFactory.create(
            type="lesson",
            **cls.lesson_location_data
        )
        cls.lesson_data = {
            'title': "Test Lesson.",
            'started_at': "2022-08-17T10:00",
            'finished_at': "2022-08-17T12:00",
            'description': "This is lesson for test.",
            'price': 25000,
            'recruit_number': 25,
            'academy': cls.academy.id,
            'location': cls.lesson_location_data,
            'genre': Genre.objects.get(name="hiphop").id,
            'mentors': [mentor.id for mentor in cls.mentors]
        }
        cls.lesson = LessonFactory.create(
            genre=Genre.objects.get(name="hiphop"),
            academy=cls.academy,
            mentor=cls.mentors,
            location=cls.lesson_location
        )
        
    def test_create_lesson(self):
        """
        Test Create Lesson and Errors.
        - Cases
            1. Successfully create lesson.
            2. Not mentor.
            3. No location field.
            4. No mentors field.
            5. No genre field.
            6. Started_at field later than finished_at.
            7. Negative price field.
            8. Negative recruit_number field.
            9. No title field.
            10. Wrong started_at field.
            11. Wrong finished_at field.
        """
        # 1. Successfully create lesson.
        data = self.lesson_data.copy()
        mentor_token = self.mentors_tokens[0]
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        # 2. Not mentor.
        mentee_token = self.mentees_tokens[0]
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentee_token)
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.json()
        self.assertEqual(data['detail'], "Only mentor can create lesson.")

        # 3. No location field.
        data = self.lesson_data.copy()
        data.pop('location')
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "location required.")

        # 4. No mentors field.
        data = self.lesson_data.copy()
        data.pop('mentors')
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "mentors required.")

        # 5. No genre field.
        data = self.lesson_data.copy()
        data.pop('genre')
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "genre required.")

        # 6. Started_at field later than finished_at.
        data = self.lesson_data.copy()
        data['started_at'] = "2022-08-17T12:01"
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "finished_at should be later than started_at.")

        # 7. Negative price field.
        data = self.lesson_data.copy()
        data['price'] = -10000
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['price'], ['Ensure this value is greater than or equal to 0.'])

        # 8. Negative recruit_number field.
        data = self.lesson_data.copy()
        data['recruit_number'] = -5
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['recruit_number'], ['Ensure this value is greater than or equal to 0.'])

        # 9. No title field.
        data = self.lesson_data.copy()
        data.pop('title')
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['title'], ['This field is required.'])

        # 10. Wrong started_at field.
        data = self.lesson_data.copy()
        data['started_at'] = "2022-08-2103:00"
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['started_at'], ['Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm.'])

        # 11. Wrong finished_at field.
        data = self.lesson_data.copy()
        data['finished_at'] = "2022-08-21-03-00"
        response = self.client.post(
            '/lesson/', 
            data=data, 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['finished_at'], ['Datetime has wrong format. Use one of these formats instead: YYYY-MM-DDThh:mm.'])

    def test_retrieve_lesson(self):
        """
        Test Retrieve Lesson.
        """
        mentor_token = self.mentors_tokens[0]
        response = self.client.get(
            f'/lesson/{self.lesson.id}/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()

        self.assertEqual(data['title'], self.lesson.title)
        self.assertEqual(data['description'], self.lesson.description)
        self.assertEqual(data['started_at'], self.lesson.started_at.strftime("%Y-%m-%dT%H:%M"))
        self.assertEqual(data['finished_at'], self.lesson.finished_at.strftime("%Y-%m-%dT%H:%M"))
        self.assertEqual(data['price'], self.lesson.price)
        self.assertEqual(data['recruit_number'], self.lesson.recruit_number)
        self.assertEqual(len(data['mentors']), 3)
        self.assertEqual(data['academy']['id'], self.academy.id)
        self.assertEqual(data['genre'], "hiphop")
        self.assertEqual(data['location']['id'], self.lesson_location.id)
        self.assertEqual(data['location']['detail'], self.lesson_location.detail)
        self.assertEqual(data['location']['description'], self.lesson_location.description)
        self.assertEqual(data['location']['district'], self.lesson_location.district)
        self.assertEqual(data['location']['city'], self.lesson_location.city)

    def test_delete_lesson(self):
        """
        Test Delete Lesson.
        - Cases
            1. Only the lesson's mentors can delete it.
            2. Successfully delete the lesson.
        """
        deleted_lesson = LessonFactory.create(
            genre=Genre.objects.get(name="hiphop"),
            academy=self.academy,
            mentor=self.mentors[:2]
        )
        mentor_token = self.mentors_tokens[0]

        # 2. Successfully delete the lesson.
        response = self.client.delete(
            f'/lesson/{deleted_lesson.id}/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentor_token)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_participate_lesson(self):
        """
        Test Participate Lesson and Errors.
        - Cases
            1. Successfully participate the lesson.
            2. Not mentee.
            3. Lesson overcrowded.
            4. Already participated.
            5. Lesson overdue.
            6. Lesson does not exist.
        """
        lesson = LessonFactory.create(
            genre=Genre.objects.get(name="hiphop"),
            academy=self.academy,
            mentor=self.mentors[:2],
            recruit_number=1,
            started_at=datetime.now()+timedelta(hours=1),
            finished_at=datetime.now()+timedelta(hours=3)
        )
        mentee_token = self.mentees_tokens[0]
        mentee = self.mentees[0]

        # 1. Successfully participate the lesson.
        before_recruit_num = lesson.recruit_number
        before_courses_cnt = mentee.mentee.courses_count
        response = self.client.get(
            f'/lesson/{lesson.id}/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentee_token)
        lesson.refresh_from_db()
        mentee.mentee.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.recruit_number, before_recruit_num-1)
        self.assertEqual(mentee.mentee.courses_count, before_courses_cnt+1)
        self.assertIn(mentee.id, lesson.mentee.all().values_list('id', flat=True))

        # 2. Not mentee.
        response = self.client.get(
            f'/lesson/{lesson.id}/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentors_tokens[0])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.json()
        self.assertEqual(data['detail'], "Only mentee can participate lesson.")

        # 3. Lesson overcrowded.
        response = self.client.get(
            f'/lesson/{lesson.id}/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentees_tokens[1])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "Lesson overcrowded.")

        # 4. Already participated.
        response = self.client.get(
            f'/lesson/{lesson.id}/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentee_token)
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        data = response.json()
        self.assertEqual(data['detail'], "Already participated.")

        # 5. Lesson overdue.
        lesson.started_at = datetime.now() - timedelta(hours=1)
        lesson.save()
        response = self.client.get(
            f'/lesson/{lesson.id}/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentees_tokens[1])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "Lesson overdue.")

        # 6. Lesson does not exist.
        response = self.client.get(
            '/lesson/9999/participate/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentees_tokens[1])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data['detail'], "Lesson does not exist.")

    def test_cancel_lesson(self):
        """
        Test Cancel Lesson and Errors.
        - Cases
            1. Cancel overdue.
            2. Successfully cancel the lesson.
            3. Not mentee.
            4. Not participated.
            5. Lesson does not exist.
        """
        lesson = LessonFactory.create(
            genre=Genre.objects.get(name="hiphop"),
            academy=self.academy,
            mentor=self.mentors[:2],
            recruit_number=0,
            started_at=datetime.now()+timedelta(hours=1),
            finished_at=datetime.now()+timedelta(hours=3),
            mentee=self.mentees[:2]
        )
        mentee_token = self.mentees_tokens[0]
        mentee = self.mentees[0]
        mentee.mentee.courses_count = 1
        mentee.mentee.save()
        mentee_2 = self.mentees[1]
        mentee_2.mentee.courses_count = 1
        mentee_2.mentee.save()

        # 1. Successfully participate the lesson.
        before_recruit_num = lesson.recruit_number
        before_courses_cnt = mentee.mentee.courses_count
        response = self.client.put(
            f'/lesson/{lesson.id}/cancel/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentee_token)
        lesson.refresh_from_db()
        mentee.mentee.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(lesson.recruit_number, before_recruit_num+1)
        self.assertEqual(mentee.mentee.courses_count, before_courses_cnt-1)
        self.assertNotIn(mentee.id, lesson.mentee.all().values_list('id', flat=True))

        # 2. Not mentee.
        response = self.client.put(
            f'/lesson/{lesson.id}/cancel/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentors_tokens[0])
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.json()
        self.assertEqual(data['detail'], "Only mentee can cancel lesson.")

        # 3. Not participated.
        response = self.client.put(
            f'/lesson/{lesson.id}/cancel/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentees_tokens[2])
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data['detail'], "Not participated.")

        # 4. Cancel overdue.
        lesson.started_at = datetime.now() + timedelta(minutes=29)
        lesson.save()
        response = self.client.put(
            f'/lesson/{lesson.id}/cancel/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=self.mentees_tokens[1])
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "Cancel overdue.")

        # 5. Lesson does not exist.
        response = self.client.put(
            '/lesson/9999/cancel/', 
            content_type="application/json",
            HTTP_AUTHORIZATION=mentee_token)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        data = response.json()
        self.assertEqual(data['detail'], "Lesson does not exist.")

