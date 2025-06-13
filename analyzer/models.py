# from django.db import models
#
# # Create your models here.
#
# class Analysis(models.Model):
#     url         = models.URLField()
#     checked_at  = models.DateTimeField(auto_now_add=True)
#     title       = models.CharField(max_length=200, blank=True)
#     meta_desc   = models.CharField(max_length=300, blank=True)
#     h1_count    = models.IntegerField(default=0)
#     missing_alt = models.IntegerField(default=0)
#     status_code = models.IntegerField(default=0)
#
#     def __str__(self):
#         return f"{self.url} @ {self.checked_at:%Y-%m-%d %H:%M}"
#
