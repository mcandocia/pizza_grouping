from __future__ import unicode_literals

from django.db import models

# Create your models here.

class Survey(models.model):
    title = models.CharField(max_length=128)
    description = models.TextField(blank=True, null=True)
    
    allow_public = models.BooleanField(default=False)
    modified_from_default=models.BooleanField(default=False)

    # in order to create a general survey for my own purposes
    # I will enforce a strict limit only in the code (both local and server-side), not the model
    max_participants = models.IntegerField(default=256)
    is_full = models.BooleanField(default=False)

    # first 8 hash based on number
    # second 8 randomly generated
    slug = models.CharField(max_length=24)

    # if False, pairs together pizza adversaries
    use_min_distance = models.BooleanField(default=True)

    timestamp = models.DateTimeField('survey created')

    expiration_date = models.DateTimeField('date set to expire')

    is_expired = models.BooleanField(default=False)

    has_topping_preferences = models.BooleanField(default=True)
    has_restrictions = models.BooleanField(default=True)
    
    has_hunger_level = models.BooleanField(default=False)
    has_pizza_style = models.BooleanField(default=False)
    has_pizza_places = models.BooleanField(default=False)

    # allow demographic responses, or remove the distraction
    allow_demographic_response = models.BooleanField(default=True)

    def __str__(self):
        return '{title} - {slug} - {max_participants}'.format(
            title=self.title,
            slug=self.slug,
            max_participants=self.max_participants
        )
    

class SurveyQuestion(models.model):
    survey = models.ForeignKey(Survey)
    # main_grid
    # hunger
    # restrictions
    # pizza style
    # place to order from
    question_type = models.CharField(max_length=8)

    # This will be a simple option, as the question_type takes care of the question's placement
    question_text = models.CharField(max_length=64)

    # whether or not this is a question that is part of the standard
    # group
    is_standard = models.BooleanField(default=True)
    

class SurveyResponse(models.model):
    survey = models.ForeignKey(Survey)
    name = models.CharField(max_length=32)
    timestamp = models.DateTimeField('response entered')
    
    allow_public = models.BooleanField(default=False)
    has_taken_survey_before = models.BooleanField(default=False)

    hide = models.BooleanField(default=False)

    # these are a few extra, optional data fields that can be used for storing preferences
    gender = models.CharField(max_length=1, blank=True, null=True)
    age_group = models.CharField(max_length=5, blank=True, null=True)
    state = models.CharField(max_length=32, blank=True, null=True)
    country = models.CharField(max_length=32, blank=True, null=True)

    # rating of pizza in general on scale of 1-6
    pizza_rating = models.IntegerField(min_value=1, max_value=6, blank=True, null=True)

class SurveyQuestionResponse(models.model):
    survey = models.ForeignKey(Survey)
    survey_question = models.ForeignKey(SurveyQuestion)
    survey_response = models.ForeignKey(SurveyResponse)
    
    value = models.CharField(max_length=32)

    
