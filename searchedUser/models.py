from django.db import models

class SearchedUser(models.Model):
    user = models.ForeignKey(
        'votarkUser.VotarkUser',
        related_name='userSearches',
        on_delete=models.SET_NULL,
        null=True,
        blank=False
    )
    searchedUser = models.ForeignKey(
        'votarkUser.VotarkUser',
        related_name='searched',
        on_delete=models.SET_NULL,
        null=True,
        blank=False
    )