from django.contrib.auth import get_user_model
from django.test import TestCase
from accounts.models import UserProfile
from academics.models import Subject, Course

User = get_user_model()

class RolePortalTests(TestCase):
    def make_user(self, username, role, password='TestPass123'):
        user = User.objects.create_user(username=username, password=password, first_name=username.title())
        profile, _ = UserProfile.objects.get_or_create(user=user)
        profile.role = role
        profile.class_name = 'Class 10' if role == 'STUDENT' else ''
        profile.division = 'A' if role == 'STUDENT' else ''
        profile.save()
        return user

    def test_dashboards_are_role_specific(self):
        cases = [
            ('admin_user', 'ADMIN', 'Institution overview'),
            ('teacher_user', 'TEACHER', 'Course management'),
            ('student_user', 'STUDENT', 'MY LEARNING'),
            ('parent_user', 'PARENT', 'FAMILY SPACE'),
        ]
        for username, role, expected in cases:
            with self.subTest(role=role):
                user = self.make_user(username, role)
                self.client.force_login(user)
                response = self.client.get('/')
                self.assertEqual(response.status_code, 200)
                self.assertContains(response, expected)
                self.client.logout()

    def test_student_cannot_open_teacher_course_creation(self):
        student = self.make_user('student_role', 'STUDENT')
        self.client.force_login(student)
        response = self.client.get('/courses/new/')
        self.assertEqual(response.status_code, 403)

    def test_teacher_can_create_course_and_owner_is_set_automatically(self):
        teacher = self.make_user('teacher_role', 'TEACHER')
        subject = Subject.objects.create(name='Mathematics')
        self.client.force_login(teacher)
        response = self.client.post('/courses/new/', {
            'title': 'Fractions', 'subject': subject.pk, 'description': 'Fraction basics',
            'module_name': 'Unit 1', 'class_name': 'Class 10', 'division': 'A',
            'academic_year': '2026-2027', 'is_published': 'on',
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Course.objects.filter(title='Fractions', teacher=teacher, is_published=True).exists())

    def test_teacher_cannot_edit_another_teachers_course(self):
        teacher_one = self.make_user('teacher_one', 'TEACHER')
        teacher_two = self.make_user('teacher_two', 'TEACHER')
        subject = Subject.objects.create(name='Science')
        course = Course.objects.create(title='Science basics', subject=subject, teacher=teacher_one, is_published=True)
        self.client.force_login(teacher_two)
        response = self.client.get(f'/courses/{course.pk}/edit/')
        self.assertEqual(response.status_code, 403)
