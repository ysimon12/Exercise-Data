from django.db import models
from django.contrib.auth.models import User

class PoseTimeSeries(models.Model):
    original_video = models.FileField(blank=True, upload_to='original')
    created_at = models.DateTimeField(auto_now_add=True)
    name = models.TextField(default="Unknown")
    label = models.TextField(default="Unknown")
    feedback = models.TextField(null=True)

class FormCheck(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    original_video = models.FileField(blank=True,upload_to='original')
    skeleton_video = models.FileField(blank=True, upload_to='skeleton')
    prediction = models.TextField(default="Unknown")
    created_at = models.DateTimeField(auto_now_add=True)
    additional_feedback = models.TextField(null=True)
    nearest1 = models.ForeignKey(PoseTimeSeries, on_delete=models.CASCADE, null=True, related_name='near1+')
    nearest2 = models.ForeignKey(PoseTimeSeries, on_delete=models.CASCADE, null=True, related_name='near2+')
    nearest3 = models.ForeignKey(PoseTimeSeries, on_delete=models.CASCADE, null=True, related_name='near3+')

    def get_fields(self):
        return [(field.name, field.value_to_string(self)) for field in FormCheck._meta.fields]

    def additional_feedback_as_list(self):
        if self.additional_feedback:
            return self.additional_feedback.split(":")
        return []



