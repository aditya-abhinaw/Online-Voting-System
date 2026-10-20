
import base64
import io

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator

from django.contrib import messages
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from django.db.models import Count
from django.shortcuts import get_object_or_404, redirect, render

from .forms import RegisterForm, VoteForm
from .models import Election, Vote


def home(request):
    elections = Election.objects.order_by('-start_time')
    voted_ids = set()

    if request.user.is_authenticated:
        voted_ids = set(
            Vote.objects.filter(user=request.user)
            .values_list('election_id', flat=True)
        )

    return render(
        request,
        'home.html',
        {
            'elections': elections,
            'voted_ids': voted_ids,
        }
    )


def register(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = RegisterForm(request.POST or None)

    if request.method == 'POST' and form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, 'Registration successful.')
        return redirect('home')

    return render(request, 'register.html', {'form': form})


@login_required
def election_detail(request, pk):
    election = get_object_or_404(Election, pk=pk)

    already_voted = Vote.objects.filter(
        user=request.user,
        election=election
    ).exists()

    if request.method == 'POST':
        if already_voted:
            messages.error(
                request,
                'You have already voted in this election.'
            )
            return redirect('election_detail', pk=pk)

        if not election.is_open:
            messages.error(
                request,
                'This election is not open for voting.'
            )
            return redirect('election_detail', pk=pk)

        form = VoteForm(election, request.POST)

        if form.is_valid():
            try:
                with transaction.atomic():
                    Vote.objects.create(
                        user=request.user,
                        election=election,
                        candidate=form.cleaned_data['candidate']
                    )
            except IntegrityError:
                messages.error(
                    request,
                    'You have already voted in this election.'
                )
                return redirect('election_detail', pk=pk)

            messages.success(
                request,
                'Your vote has been recorded.'
            )
            return redirect('results', pk=pk)
    else:
        form = VoteForm(election)

    return render(
        request,
        'election_detail.html',
        {
            'election': election,
            'form': form,
            'already_voted': already_voted,
        }
    )


def make_chart(rows):
    fig, ax = plt.subplots(figsize=(7, 4))

    ax.bar(
        [row['name'] for row in rows],
        [row['votes'] for row in rows]
    )

    ax.set_ylabel('Votes')
    ax.set_title('Election Results')
    ax.yaxis.set_major_locator(MaxNLocator(integer=True))
    fig.tight_layout()

    buffer = io.BytesIO()
    fig.savefig(buffer, format='png', bbox_inches='tight')
    plt.close(fig)

    return base64.b64encode(buffer.getvalue()).decode()


def results(request, pk):
    election = get_object_or_404(Election, pk=pk)

    candidates = election.candidates.annotate(
        vote_count=Count('votes')
    ).order_by('-vote_count', 'name')

    total = sum(candidate.vote_count for candidate in candidates)

    rows = [
        {
            'name': candidate.name,
            'votes': candidate.vote_count,
            'percent': (
                round(candidate.vote_count * 100 / total, 1)
                if total else 0
            ),
        }
        for candidate in candidates
    ]

    chart = make_chart(rows) if total else None

    return render(
        request,
        'results.html',
        {
            'election': election,
            'rows': rows,
            'total': total,
            'chart': chart,
        }
    )
