from django.db import models

# Create your models here.

class Product(models.Model):
    '''
        AutoField is an IntegerField that automatically increments according to available IDs
    '''
    product_id = models.AutoField # We dont make it primary key. So django automatically makes
                                  # a primary_key by name id
    product_name = models.CharField(max_length = 50)
    category = models.CharField(max_length=50,default="")
    subcategory = models.CharField(max_length=50,default="")
    price = models.IntegerField(default=0)
    desc = models.CharField(max_length = 300)   # Description
    pub_date = models.DateField()     # Publish Date
    image = models.ImageField(upload_to = 'shop/images',default="")

    def __str__(self):
        return self.product_name


class Contact(models.Model):
    '''
        AutoField is an IntegerField that automatically increments according to available IDs
    '''
    msg_id = models.AutoField(primary_key = True)
    name = models.CharField(max_length = 50)
    email = models.CharField(max_length=50,default="")
    phone = models.CharField(max_length=50,default="")
    desc = models.CharField(max_length = 500,default="")   # Description

    def __str__(self):
        return self.name

class Orders(models.Model):
    order_id = models.AutoField(primary_key = True)
    amount = models.IntegerField(default=0)
    items_json = models.CharField(max_length = 5000);
    name = models.CharField(max_length = 60);
    email = models.CharField(max_length = 100);
    address = models.CharField(max_length = 500);
    city = models.CharField(max_length = 60);
    state = models.CharField(max_length = 60);
    # Don't use simply zip variable bcz zip is also inbuilt method
    zip_code = models.CharField(max_length = 60);
    phone = models.CharField(max_length = 60);


class OrderUpdate(models.Model):
    update_id = models.AutoField(primary_key = True)
    order_id = models.IntegerField(default = "")
    update_desc = models.CharField(max_length = 1000)
    timestamp = models.DateField(auto_now_add = True)

    def __str__(self):
        return self.update_desc[0:7]+"..."
