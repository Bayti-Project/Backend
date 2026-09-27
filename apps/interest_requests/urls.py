from django.urls import path

from apps.interest_requests.views import (
    InterestRequestCreateView,
    InterestRequestStatusView,
    OwnerInterestRequestListView,
)

app_name = 'interest_requests'

urlpatterns = [
    path(
        'properties/<int:pk>/interest-request',
        InterestRequestCreateView.as_view(),
        name='interest-request-create',
    ),
    path(
            'interest-request/<int:pk>/status',
            InterestRequestStatusView.as_view(),
            name='interest-request-status',
            
        ),
    path(
        'owner/interest-requests',
        OwnerInterestRequestListView.as_view(),
        name='owner-interest-request-list',
    ),
]