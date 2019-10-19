from django.db import models

# Create your models here.


class Blogpost(models.Model):
    '''
        AutoField is an IntegerField that automatically increments according to available IDs
    '''
    post_id = models.AutoField(primary_key = True)
    title = models.CharField(max_length=100,default ="")
    head0 = models.CharField(max_length=500,default ="")
    chead0 = models.CharField(max_length=5000,default ="")
    head1 = models.CharField(max_length=500,default ="")
    chead1 = models.CharField(max_length=5000,default ="")
    head2 = models.CharField(max_length=500,default ="")
    chead2 = models.CharField(max_length=5000,default ="")
    pub_date = models.DateField()     # Publish Date
    thumbnail = models.ImageField(upload_to = 'shop/images',default="")

    def __str__(self):
        return self.title
