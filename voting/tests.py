
from datetime import timedelta

from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone

from .models import Election, Candidate, Vote


class VotingSystemTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            password='TestPass123!'
        )

        self.election = Election.objects.create(
            title='Student Council Election',
            description='Test election',
            start_time=timezone.now() - timedelta(hours=1),
            end_time=timezone.now() + timedelta(days=1),
            is_active=True
        )

        self.candidate = Candidate.objects.create(
            election=self.election,
            name='Candidate A'
        )

    def test_homepage_displays_election(self):
        response = self.client.get(reverse('home'))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.election.title)

    def test_user_can_register(self):
        response = self.client.post(
            reverse('register'),
            {
                'username': 'newuser',
                'email': 'newuser@example.com',
                'password1': 'StrongPass123!abc',
                'password2': 'StrongPass123!abc',
            }
        )

        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            User.objects.filter(username='newuser').exists()
        )

    def test_user_can_vote_once(self):
        self.client.force_login(self.user)

        response = self.client.post(
            reverse('election_detail', args=[self.election.pk]),
            {'candidate': self.candidate.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Vote.objects.filter(
                user=self.user,
                election=self.election
            ).count(),
            1
        )

    def test_duplicate_vote_is_prevented(self):
        self.client.force_login(self.user)

        Vote.objects.create(
            user=self.user,
            election=self.election,
            candidate=self.candidate
        )

        response = self.client.post(
            reverse('election_detail', args=[self.election.pk]),
            {'candidate': self.candidate.pk}
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(
            Vote.objects.filter(
                user=self.user,
                election=self.election
            ).count(),
            1
        )
