from django.db import models
from django.contrib.auth.models import User
from django.db.models import Max

# Create your models here.

def user_directory_path(instance, filename):
    # путь, куда будет осуществлена загрузка MEDIA_ROOT/user_<id>/<filename>
    return 'user_{0}/{1}'.format(instance.user.username, filename)

class Files(models.Model):
    user = models.ForeignKey(to=User,null=True,on_delete=models.SET_NULL)
    upload = models.FileField(upload_to=user_directory_path)

    def save(self, *args, **kwargs):
        # i moved the logic to signals

        # if not self.slug:
        # self.slug = slugify(self.title)
        super(Files, self).save(*args, **kwargs)

class BaseWord(models.Model):
    """ Celery task info"""
    name=models.CharField(max_length=100)
    user = models.CharField(max_length=100,default=None)
    uid = models.IntegerField(default=None,null=True)
    type = models.TextField(default=None)
    file = models.FileField(upload_to=user_directory_path,default=None,null=True)
    file_state = models.FileField(upload_to=user_directory_path,default=None,null=True)
    file_acrhiv = models.FileField(upload_to=user_directory_path,default=None,null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name





class BaseTask(models.Model):
    """ Celery task info"""
    name = models.CharField(max_length=100)
    is_success = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name




class BaseParsingResult(models.Model):
    """ Parsing result details"""
    task_id = models.ForeignKey(
        BaseWord,
        blank=True,
        null=True,
        on_delete=models.PROTECT,
        related_name="links"
    )
    sites = models.TextField(blank=True, null=True)
    user = models.CharField(max_length=100, blank=True, null=True)
    uid = models.IntegerField(default=None,null=True)
    file_word = models.FileField(blank=True, null=True)
    number_id = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, null=True)
    date_ot = models.DateField(blank=True, null=True)
    date_do = models.DateField(blank=True, null=True)
    result = models.FileField(blank=True, null=True)
    result_text = models.TextField(blank=True, null=True)
    task_type = models.CharField(blank=True, max_length=64, null=True)