from datetime import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from books.models import Book
from books.tests.test_books import sample_book
from borrowings.models import Borrowing
from borrowings.serializers import (
    BorrowingCreateSerializer,
    BorrowingDetailSerializer,
    BorrowingSerializer,
)

BORROWING_URL = reverse("borrowing:borrowing-list")


def detail_url(borrowing_id: int):
    return reverse("borrowing:borrowing-detail", args=[borrowing_id])


def return_url(borrowing_id: int):
    """Return URL for recipe borrowing return"""
    return reverse("borrowing:borrowing-return-borrowing", args=[borrowing_id])


def sample_user(**params):
    defaults = {
        "email": "test@user.com",
        "password": "password",
    }
    defaults.update(params)

    return get_user_model().objects.create_user(**defaults)


def sample_borrowing(**params):
    book = sample_book()

    defaults = {
        "borrow_date": "2024-07-02",
        "expected_return_date": "2024-07-05",
        "book": book,
        "user_id": 1,
    }
    defaults.update(params)

    return Borrowing.objects.create(**defaults)


class UnauthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        res = self.client.get(BORROWING_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class AuthenticatedBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "test@user.com",
            "PassWord",
        )
        self.client.force_authenticate(self.user)

    def test_list_borrowings(self):
        sample_borrowing()
        sample_borrowing()

        res = self.client.get(BORROWING_URL)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_borrowing_detail(self):
        borrowing = sample_borrowing()

        url = detail_url(borrowing.id)
        res = self.client.get(url)

        serializer = BorrowingDetailSerializer(borrowing)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_return_borrowing(self):
        borrowing = sample_borrowing()

        self.client.post(return_url(borrowing.id))

        instance = Borrowing.objects.get(pk=borrowing.id)
        current = datetime.now()
        current_date = current.date()

        self.assertEqual(instance.actual_return_date, current_date)

    def test_return_borrowing_limited(self):
        borrowing = sample_borrowing()

        self.client.post(return_url(borrowing.id))
        res = self.client.post(return_url(borrowing.id))

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_add_1_to_book_inventory_on_returning(self):
        borrowing = sample_borrowing()
        book = borrowing.book
        inventory_expected = book.inventory + 1

        self.client.post(return_url(borrowing.id))

        instance = Book.objects.get(pk=book.id)
        inventory_actual = instance.inventory

        self.assertEqual(inventory_actual, inventory_expected)


class AdminBorrowingTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            "admin@admin.com", "password", is_staff=True
        )
        self.client.force_authenticate(self.user)

    def test_list_all_existing_borrowings(self):
        user = sample_user()

        sample_borrowing(user_id=user.id)
        sample_borrowing(user_id=user.id)
        sample_borrowing(user_id=self.user.id)

        borrowings = Borrowing.objects.all()
        serializer = BorrowingSerializer(borrowings, many=True)

        res = self.client.get(BORROWING_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(serializer.data, res.data)

    def test_filter_borrowings_by_user_id(self):
        user = sample_user()

        borrowing_1 = sample_borrowing(user_id=user.id)
        borrowing_2 = sample_borrowing(user_id=user.id)
        borrowing_3 = sample_borrowing(user_id=self.user.id)

        res = self.client.get(BORROWING_URL, {"user_id": user.id})

        serializer1 = BorrowingSerializer(borrowing_1)
        serializer2 = BorrowingSerializer(borrowing_2)
        serializer3 = BorrowingSerializer(borrowing_3)

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)

    def test_filter_borrowings_by_is_active(self):
        borrowing_1 = sample_borrowing()
        borrowing_2 = sample_borrowing()
        borrowing_3 = sample_borrowing()

        serializer1 = BorrowingSerializer(borrowing_1)
        serializer2 = BorrowingSerializer(borrowing_2)
        serializer3 = BorrowingSerializer(borrowing_3)

        self.client.post(return_url(borrowing_3.id))
        res = self.client.get(BORROWING_URL, {"is_active": True})

        self.assertIn(serializer1.data, res.data)
        self.assertIn(serializer2.data, res.data)
        self.assertNotIn(serializer3.data, res.data)
