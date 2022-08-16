from django.test import TestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from factory.django import DjangoModelFactory
from rest_framework.authtoken.models import Token
from faker import Faker
from user.profile.tests import MentorFactory, MenteeFactory
from user.core.genre.utils import generate_genres
from util.location.tests import LocationFactory
from user.core.academy.tests import AcademyFactory
from user.core.genre.models import Genre

User = get_user_model()

class UserFactory(DjangoModelFactory):
    class Meta:
        model = User

    idx = 0
    @classmethod
    def create(cls, **kwargs) -> User:
        fake = Faker("ko_KR")

        user = User.objects.create(
            email=kwargs.get("email", f"test{cls.idx}@snu.ac.kr"),
            password=kwargs.get("password", fake.password()),
            username=kwargs.get("username", fake.name()),
            first_name=kwargs.get("first_name", fake.first_name()),
            last_name=kwargs.get("last_name", fake.last_name()),
            birth=kwargs.get("birth", fake.date_of_birth()),
            gender=kwargs.get("gender", fake.random_choices(elements=('male', 'female'), length=1)[0]),
            contact=kwargs.get("contact", fake.phone_number()),
            mentor=kwargs.get("mentor"),
            mentee=kwargs.get("mentee")
        )
        token, created = Token.objects.get_or_create(user=user)

        cls.idx += 1
        return user

    @classmethod
    def bulk_create(cls, **kwargs) -> User:
        fake = Faker("ko_KR")
        users_list = []
        for i in range(kwargs['count']):
            user = User(
                email=kwargs.get("email", f"test{cls.idx}@snu.ac.kr"),
                password=kwargs.get("password", fake.password()),
                username=kwargs.get("username", fake.name()),
                first_name=kwargs.get("first_name", fake.first_name()),
                last_name=kwargs.get("last_name", fake.last_name()),
                birth=kwargs.get("birth", fake.date_of_birth()),
                gender=kwargs.get("gender", fake.random_choices(elements=('male', 'female'), length=1)[0]),
                contact=kwargs.get("contact", fake.phone_number()),
                mentor=kwargs.get("mentor"),
                mentee=kwargs.get("mentee")
            )
            users_list.append(user)
            cls.idx += 1
        users = User.objects.bulk_create(users_list)
        for user in users:
            token, created = Token.objects.get_or_create(user=user)
        return users

        
class UserTestCase(TestCase):
    """
    # Test User APIs.
        [POST] /user
        []
        []
        []
        []
    """

    @classmethod
    def setUpTestData(cls) -> None:
        cls.genres_id = generate_genres()
        cls.mentor = UserFactory.create(mentor=MentorFactory.create())
        cls.mentor_token = "Token " + str(cls.mentor.auth_token)
        cls.mentee = UserFactory.create(mentee=MenteeFactory.create())
        cls.mentee_token = "Token " + str(cls.mentee.auth_token)
        cls.location = LocationFactory.create(
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
            location=cls.location
        )
        cls.base_data = {
            "email": "jaejae2374@test.com",
            "password": "2wogus",
            "username": "이재현",
            "first_name": "jaehyun",
            "last_name": "lee",
            "birth": "1997-02-03",
            "gender": "male",
            "contact": "01025911955"
        }
        cls.mentor_data = {
            "started_at": "2016-02",
            "description": "사자후장입니다.",
            "genres": cls.genres_id[:2],
            "academies": [cls.academy.id]
        }
        cls.mentee_data = {
            "started_at": "2016-02",
            "description": "사자후장입니다.",
            "genres": cls.genres_id[3:6],
        }


    def test_create_user_mentor(self):
        """
        Test Create Mentor User.
        """
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_create_user_mentee(self):
        """
        Test Create Mentee User.
        """
        data = self.base_data.copy()
        data['mentee'] = self.mentee_data.copy()
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)


    def test_create_user_error(self):
        """
        Test Create User Errors.
        - Cases
            1. Does not choose profile [mentor, mentee].
            2. Wrong birth format.
            3. Wrong gender [male, female].
        """
        # 1. Does not choose profile [mentor, mentee].
        data = self.base_data.copy()
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'choose one between mentor, mentee.')

        # 2. Wrong birth format.
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['birth'] = "1997.02.03"
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['birth'], ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.'])

        # 3. Wrong gender [male, female].
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['gender'] = "man"
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'wrong gender. [male, female]')


    def test_create_user_mentor_error(self):
        """
        Test Create Mentor User Errors.
        - Cases
            1. No genres field.
            2. No academies field.
            3. No started_at field.
            4. Wrong started_at field.
        """
        # 1. No genres field.
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['mentor'].pop('genres')
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'genres required.')

        # 2. No academies field.
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['mentor'].pop('academies')
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'academies required.')

        # 3. No started_at field.
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['mentor'].pop('started_at')
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['started_at'], ['This field is required.'])

        # 4. Wrong started_at field.
        data = self.base_data.copy()
        data['mentor'] = self.mentor_data.copy()
        data['mentor']['started_at'] = "2019-02-03"
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['started_at'], ['Date has wrong format. Use one of these formats instead: YYYY-MM.'])


    def test_create_user_mentee_error(self):
        """
        Test Create Mentee User Errors.
        - Cases
            1. No genres field.
            2. No started_at field.
            3. Wrong started_at field.
        """
        # 1. No genres field.
        data = self.base_data.copy()
        data['mentee'] = self.mentee_data.copy()
        data['mentee'].pop('genres')
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'genres required.')

        # 2. No started_at field.
        data = self.base_data.copy()
        data['mentee'] = self.mentee_data.copy()
        data['mentee'].pop('started_at')
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['started_at'], ['This field is required.'])

        # 3. Wrong started_at field.
        data = self.base_data.copy()
        data['mentee'] = self.mentee_data.copy()
        data['mentee']['started_at'] = "2019-02-03"
        response = self.client.post(
            '/user/', 
            data=data, 
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['started_at'], ['Date has wrong format. Use one of these formats instead: YYYY-MM.'])


    def test_update_user(self):
        """
        Test Update User and Errors.
        - Cases
            1. Successfully update.
            2. Wrong gender field.
            3. Wrong birth field.
            4. User Not Found.
        """
        # 1. Successfully update.
        user_id = self.mentor.id
        modified_data = {
            "username": "이재현",
            "first_name": "jaehyun",
            "last_name": "lee",
            "birth": "1997-02-03",
            "gender": "male",
            "contact": "01025911955"
        }
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['username'], modified_data['username'])
        self.assertEqual(data['first_name'], modified_data['first_name'])
        self.assertEqual(data['last_name'], modified_data['last_name'])
        self.assertEqual(data['birth'], modified_data['birth'])
        self.assertEqual(data['gender'], modified_data['gender'])
        self.assertEqual(data['contact'], modified_data['contact'])

        # 2. Wrong gender field.
        modified_data["gender"] = "woman"
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], 'wrong gender. [male, female]')
        modified_data["gender"] = "male"

        # 3. Wrong birth field.
        modified_data["birth"] = "2021.01.22"
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['birth'], ['Date has wrong format. Use one of these formats instead: YYYY-MM-DD.'])
        modified_data["birth"] = "1997-02-03"

        # 4. User Not Found.
        response = self.client.put(
            f'/user/9999/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mentor_user(self):
        """
        Test Update Mentor User and Errors.
        - Cases
            1. Successfully update.
            2. Not Mentor.
            3. Wrong started_at field.
        """
        # 1. Successfully update.
        user_id = self.mentor.id
        modified_data = {
            "mentor": {
                "academy_delete": list(self.mentor.mentor.academy.values_list('id', flat=True)),
                "academy_add": [self.academy.id],
                "genre_delete": list(self.mentor.mentor.genre.values_list('id', flat=True)),
                "genre_add": [1, 2, 3],
                "description": "Test Update !!",
                "started_at": "2020-02"
            }
        }
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['mentor']['description'], modified_data['mentor']['description'])
        self.assertEqual(data['mentor']['started_at'], modified_data['mentor']['started_at'])
        self.assertEqual(
            list(Genre.objects.filter(id__in=modified_data['mentor']['genre_add']).values_list('name', flat=True)),
            data['mentor']['genre'])
        self.assertEqual(
            self.academy.id,
            data['mentor']['academy'][0]['id'])
        self.assertEqual(1, len(data['mentor']['academy']))

        # 2. Not Mentor.
        response = self.client.put(
            f'/user/{self.mentee.id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.json()
        self.assertEqual(data['detail'], "you are not Mentor.")

        # 3. Wrong started_at field.
        modified_data = {
            "mentor": {
                "started_at": "2020.02"
            }
        }
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data=response.json()
        self.assertEqual(data['started_at'], ['Date has wrong format. Use one of these formats instead: YYYY-MM.'])

    def test_mentee_user(self):
        """
        Test Update Mentee User and Errors.
        - Cases
            1. Successfully update.
            2. Not Mentee.
            3. Wrong started_at field.
        """
        # 1. Successfully update.
        user_id = self.mentee.id
        modified_data = {
            "mentee": {
                "genre_delete": list(self.mentee.mentee.genre.values_list('id', flat=True)),
                "genre_add": [1, 2, 3],
                "description": "Test Update !!",
                "started_at": "2020-02"
            }
        }
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['mentee']['description'], modified_data['mentee']['description'])
        self.assertEqual(data['mentee']['started_at'], modified_data['mentee']['started_at'])
        self.assertEqual(
            list(Genre.objects.filter(id__in=modified_data['mentee']['genre_add']).values_list('name', flat=True)),
            data['mentee']['genre'])

        # 2. Not Mentor.
        response = self.client.put(
            f'/user/{self.mentor.id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
        data = response.json()
        self.assertEqual(data['detail'], "you are not Mentee.")

        # 3. Wrong started_at field.
        modified_data = {
            "mentee": {
                "started_at": "2020.02"
            }
        }
        response = self.client.put(
            f'/user/{user_id}/', 
            data=modified_data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data=response.json()
        self.assertEqual(data['started_at'], ['Date has wrong format. Use one of these formats instead: YYYY-MM.'])

    def test_retrieve_user(self):
        """
        Test Retrieve User and Errors.
        - Cases
            1. Successfully retrieve mentor user.
            2. Successfully retrieve mentee user.
            3. User Not Found.
        """
        # 1. Successfully retrieve mentor user.
        user = self.mentor
        response = self.client.get(
            f'/user/{user.id}/', 
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['birth'], user.birth.strftime("%Y-%m-%d"))
        self.assertEqual(data['gender'], user.gender)
        self.assertEqual(data['contact'], user.contact)
        data_mentor = data['mentor']
        user_mentor = user.mentor
        self.assertEqual(data_mentor['started_at'], user_mentor.started_at.strftime("%Y-%m"))
        self.assertEqual(data_mentor['description'], user_mentor.description)
        self.assertEqual(len(data_mentor['academy']), user_mentor.academy.count())
        self.assertIsNotNone(data_mentor['academy'][0]['location'])
        self.assertEqual(data_mentor['genre'], list(user_mentor.genre.values_list('name', flat=True)))
        self.assertIsNone(data['mentee'])

        # 2. Successfully retrieve mentee user.
        user = self.mentee
        response = self.client.get(
            f'/user/{self.mentee.id}/', 
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['username'], user.username)
        self.assertEqual(data['first_name'], user.first_name)
        self.assertEqual(data['last_name'], user.last_name)
        self.assertEqual(data['birth'], user.birth.strftime("%Y-%m-%d"))
        self.assertEqual(data['gender'], user.gender)
        self.assertEqual(data['contact'], user.contact)
        data_mentee = data['mentee']
        user_mentee = user.mentee
        self.assertEqual(data_mentee['started_at'], user_mentee.started_at.strftime("%Y-%m"))
        self.assertEqual(data_mentee['description'], user_mentee.description)
        self.assertEqual(data_mentee['courses_count'], 0)
        self.assertEqual(data_mentee['tier'], 'Unranked')
        self.assertEqual(data_mentee['genre'], list(user_mentee.genre.values_list('name', flat=True)))
        self.assertIsNone(data['mentor'])

        # 3. User Not Found.
        response = self.client.get(
            '/user/9999/', 
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_delete_user(self):
        """
        Test Delete User.
        """
        test_user = UserFactory.create(mentor=MentorFactory.create())
        test_user_token = "Token " + str(test_user.auth_token)
        response = self.client.delete(
            f'/user/{test_user.id}/', 
            HTTP_AUTHORIZATION=test_user_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

    def test_login_user(self):
        """
        Test Login User.
        - Cases
            1. Login Success.
            2. Wrong Email.
            3. Wrong Password.
        """
        # 1. Login Success.
        body = {
            'email': self.mentor.email,
            'password': self.mentor.password
        }
        response = self.client.put(
            '/user/login/',
            data=body,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data = response.json()
        self.assertEqual(data['success'], True)
        self.assertEqual(data['token'], str(self.mentor.auth_token))

        # 2. Wrong Email.
        wrong_body = body.copy()
        wrong_body['email'] = "wrongemail"
        response = self.client.put(
            '/user/login/',
            data=wrong_body,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "이메일 또는 비밀번호가 잘못되었습니다.")

        # 3. Wrong Password.
        wrong_body = body.copy()
        wrong_body['password'] = "wrongpassword"
        response = self.client.put(
            '/user/login/',
            data=wrong_body,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        data = response.json()
        self.assertEqual(data['detail'], "이메일 또는 비밀번호가 잘못되었습니다.")

    def test_logout_user(self):
        """
        Test Logout User.
        """
        response = self.client.get(
            f'/user/logout/', 
            HTTP_AUTHORIZATION=self.mentor_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertNotEqual(self.mentor_token, self.mentor.auth_token)

    def test_mentor(self):
        """
        Test Search Mentor Users.
        """
        academy = {
            "name": "test academy"
        }
        mentor_1 = UserFactory.create(
            username="1김사장",
            mentor=MentorFactory.create(
                genre=['hiphop', 'krump'],
                academy=academy.copy()
            ))
        mentor_2 = UserFactory.create(
            username="3이사장",
            mentor=MentorFactory.create(
                genre=['hiphop', 'k-pop'],
                academy=academy.copy()
            ))
        mentor_3 = UserFactory.create(
            username="2박사장",
            mentor=MentorFactory.create(
                genre=['krump', 'k-pop'],
            ))
        data = {
            'name': "1김"
        }
        response = self.client.get(
            '/user/mentor/',
            data=data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data=response.json()
        self.assertEqual(data[0]['id'], mentor_1.id)
        self.assertEqual(data[0]['username'], mentor_1.username)
        self.assertEqual(data[0]['genre'], list(mentor_1.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[0]['academy'], list(mentor_1.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(len(data), 1)

        data = {
            'name': "사장"
        }
        response = self.client.get(
            '/user/mentor/',
            data=data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data=response.json()
        self.assertEqual(data[0]['id'], mentor_1.id)
        self.assertEqual(data[0]['username'], mentor_1.username)
        self.assertEqual(data[0]['genre'], list(mentor_1.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[0]['academy'], list(mentor_1.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(data[1]['id'], mentor_3.id)
        self.assertEqual(data[1]['username'], mentor_3.username)
        self.assertEqual(data[1]['genre'], list(mentor_3.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[1]['academy'], list(mentor_3.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(data[2]['id'], mentor_2.id)
        self.assertEqual(data[2]['username'], mentor_2.username)
        self.assertEqual(data[2]['genre'], list(mentor_2.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[2]['academy'], list(mentor_2.mentor.academy.values_list('name', flat=True)))

        data = {
            'genre': ["hiphop"]
        }
        response = self.client.get(
            '/user/mentor/',
            data=data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data=response.json()
        self.assertEqual(data[0]['id'], mentor_1.id)
        self.assertEqual(data[0]['username'], mentor_1.username)
        self.assertEqual(data[0]['genre'], list(mentor_1.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[0]['academy'], list(mentor_1.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(data[1]['id'], mentor_2.id)
        self.assertEqual(data[1]['username'], mentor_2.username)
        self.assertEqual(data[1]['genre'], list(mentor_2.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[1]['academy'], list(mentor_2.mentor.academy.values_list('name', flat=True)))
        for mentor in data:
            self.assertNotEqual(mentor['id'], mentor_3.id)

        data = {
            'genre': ["hiphop", "waacking"]
        }
        response = self.client.get(
            '/user/mentor/',
            data=data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data=response.json()
        self.assertEqual(data[0]['id'], mentor_1.id)
        self.assertEqual(data[0]['username'], mentor_1.username)
        self.assertEqual(data[0]['genre'], list(mentor_1.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[0]['academy'], list(mentor_1.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(data[1]['id'], mentor_2.id)
        self.assertEqual(data[1]['username'], mentor_2.username)
        self.assertEqual(data[1]['genre'], list(mentor_2.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[1]['academy'], list(mentor_2.mentor.academy.values_list('name', flat=True)))

        data = {
            'academy': "test"
        }
        response = self.client.get(
            '/user/mentor/',
            data=data,
            HTTP_AUTHORIZATION=self.mentee_token,
            content_type="application/json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        data=response.json()
        self.assertEqual(data[0]['id'], mentor_1.id)
        self.assertEqual(data[0]['username'], mentor_1.username)
        self.assertEqual(data[0]['genre'], list(mentor_1.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[0]['academy'], list(mentor_1.mentor.academy.values_list('name', flat=True)))
        self.assertEqual(data[1]['id'], mentor_2.id)
        self.assertEqual(data[1]['username'], mentor_2.username)
        self.assertEqual(data[1]['genre'], list(mentor_2.mentor.genre.values_list('name', flat=True)))
        self.assertEqual(data[1]['academy'], list(mentor_2.mentor.academy.values_list('name', flat=True)))
        for mentor in data:
            self.assertNotEqual(mentor['id'], mentor_3.id)
