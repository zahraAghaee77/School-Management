from django.db import models

from school.models import *
from user.models import *


class Assignment(models.Model):
    title = models.CharField(max_length=255, null=False)
    context = models.TextField(null=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=True)
    deadline = models.DateTimeField(null=False)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="assignments/", null=True, blank=True)
    answer_text = models.TextField(null=True)
    answer_file = models.FileField(upload_to="answers/", null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    lesson = models.ForeignKey(
        Lesson, on_delete=models.CASCADE, related_name="assignments_lesson", null=False
    )
    class_obj = models.ForeignKey(
        Class, on_delete=models.CASCADE, related_name="assignments_class", null=False
    )

    def __str__(self):
        return f"{self.title} - {self.context} - {self.grade}"


class Solution(models.Model):
    context = models.TextField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to="assignments/", null=True, blank=True)
    last_modified = models.DateTimeField(auto_now=True)
    grade = models.DecimalField(max_digits=5, decimal_places=2, null=False, blank=True)
    student = models.ForeignKey(
        User, related_name="solution_student", null=False, on_delete=models.CASCADE
    )
    assignment = models.ForeignKey(
        Assignment,
        related_name="solution_assignment",
        null=False,
        on_delete=models.CASCADE,
    )
