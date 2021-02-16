from django.db import models
from django.contrib.auth.models import AbstractUser


def upload_catalog_to(instance, filename):
    company_name = instance.company.name
    return 'static/catalog/%s/%s' % (company_name, filename)


def upload_company_logo_to(instance, filename):
    company_name = instance.name
    return 'static/company_logos/%s/%s' % (company_name, filename)


class Customer(AbstractUser):
    # this should extend the base user model
    email = models.EmailField('email address', unique=True)
    location = models.CharField(max_length=30, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    open_address = models.CharField(max_length=1000, blank=True, null=True)
    username = None
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = ('Customer')
        verbose_name_plural = ('Customers')


class Company(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    logo = models.FileField(
        upload_to=upload_company_logo_to, null=True, blank=True)

    country = models.CharField(max_length=500)
    city = models.CharField(max_length=500)

    def __str__(self):
        return self.name + '[{}/{}]'.format(self.city, self.country)


class Product(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    # auto add time
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    # company
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    catalog = models.ForeignKey(
        'Catalog', on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.name


class Catalog(models.Model):
    id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=500)
    company = models.ForeignKey('Company', on_delete=models.CASCADE)
    pdf_file = models.FileField(
        upload_to=upload_catalog_to, null=True, blank=True)
    # PDF FILE?
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name + ' | at Company: ' + str(self.company)


class ShoppingList(models.Model):
    id = models.AutoField(primary_key=True)
    customer = models.ForeignKey('Customer', on_delete=models.CASCADE)
    name = models.CharField(max_length=150, null=True, blank=False)
    is_deleted_offline = models.BooleanField(default=False)

    def __str__(self):
        return 'id: ' + str(self.id) + ' name: ' + self.name + ' ' + str(self.customer)


class ShoppingListItem(models.Model):
    id = models.AutoField(primary_key=True)
    shopping_list = models.ForeignKey('ShoppingList', on_delete=models.CASCADE)
    company = models.ForeignKey('Company', on_delete=models.CASCADE, null=True)
    # product = models.ForeignKey('Product', on_delete=models.CASCADE)
    text = models.CharField(max_length=400, null=True, blank=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(editable=True, null=True, blank=True)
    is_visible = models.BooleanField(default=True)
    is_checked = models.BooleanField(default=False, null=True)

    def __str__(self):
        return "id: " + str(self.id) + " text: " + self.text
