from django.db import models
from django.contrib.auth.models import AbstractUser
from api.constants import *
from django.utils import timezone
from tenant_schemas.models import TenantMixin


"""
User Model
"""
class User(AbstractUser):
    username = models.CharField(max_length=150,blank=True, null=True,unique=True)
    full_name = models.CharField(max_length=150,null=True,blank=True)
    first_name = models.CharField(max_length=150,null=True,blank=True)
    last_name = models.CharField(max_length=150,null=True,blank=True)
    email = models.EmailField("email address", null=True, blank=True)
    mobile_no = models.CharField(max_length=20, null=True, blank=True)
    profile_pic = models.ImageField(upload_to='profile_pic/', blank=True, null=True)
    address = models.TextField()
    city = models.CharField(max_length=255,blank=True,null=True)
    state = models.CharField(max_length=255,blank=True,null=True)
    age = models.CharField(max_length=255,null=True,blank=True)
    client_customer_id = models.IntegerField(null=True, blank=True, editable=True)
    uid = models.UUIDField(unique=True, editable=True, null=True, blank=True)
    country = models.CharField(max_length=255,blank=True,null=True)
    company = models.ForeignKey('CompanyInformation',on_delete=models.CASCADE,null=True,blank=True)
    role_id = models.PositiveIntegerField(default=SUPER_ADMIN,choices=USER_ROLE,null=True, blank=True)
    status = models.PositiveIntegerField(default=ACTIVE, choices=USER_STATUS,null=True, blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    customer_id = models.CharField(max_length=255,blank=True,null=True)
    test_taken = models.CharField(max_length=255,null=True,blank=True)
    notification_enable = models.BooleanField(default=True,null=True,blank=True)
    user_feedback = models.TextField(null=True,blank=True)
    user_prefrence = models.PositiveIntegerField(default=ENGLISH,choices = LANGUAGE_PREFERENCES ,null =True,blank=True)
    user_image = models.ImageField(upload_to='User_Images/', null=True, blank=True)
    face_shape = models.CharField(max_length=255,blank=True,null=True)
    health_score = models.CharField(max_length=255, blank=True,null=True)
    p_distance = models.CharField(max_length=255, blank=True,null=True)
    

    class Meta:
        db_table = 'User_table'

    def __str__(self):
            first_name = self.first_name if  self.first_name else ''
            last_name  = self.last_name if  self.last_name else ''
            return f'{first_name} {last_name}'

class CompanyInformation(TenantMixin):
    company_name = models.CharField(max_length=255,null=True,blank=True)
    official_number = models.CharField(max_length=255,null=True,blank=True)
    city = models.CharField(max_length=255,blank=True,null=True)
    state = models.CharField(max_length=255,blank=True,null=True)
    country = models.CharField(max_length=255,blank=True,null=True)
    official_website = models.URLField(null=True,blank=True)
    official_domain_email = models.EmailField(null=True, blank=True)
    business_id = models.CharField(max_length=255,null=True,blank=True)
    requirement = models.CharField(max_length=255,null=True,blank=True)
    name_of_person = models.CharField(max_length=255,null=True,blank=True)
    daily_traffic = models.CharField(max_length=255,null=True,blank=True)
    designation = models.CharField(max_length=255,null=True,blank=True)
    daily_business = models.CharField(max_length=255,null=True,blank=True)
    company_address = models.CharField(max_length=255,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    package_status = models.CharField(max_length=255,null=True,blank=True)
    company_uid = models.UUIDField(unique=True, editable=True, null=True, blank=True)

    auto_create_schema = True
 
    class Meta:  
        db_table = "Company_Information"


# class Domain(DomainMixin):
#     domain = models.CharField(max_length=255,null=True,blank=True)
#     name = models.CharField(max_length=255,null=True,blank=True)

#     class Meta:
#         db_table = "tbl_domain"




class Notification(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.CharField(max_length=255,null=True,blank=True)
    image = models.FileField(upload_to="notification_image",null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="created_by")
    users = models.ManyToManyField(User)
    is_read = models.BooleanField(default=False,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        db_table = "Notification_Information"

class ReportIssue(models.Model):
    admin_mail = models.EmailField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    subject = models.CharField(max_length=255,null=True,blank=True)
    issue_description = models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        db_table = "Report Issue"


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    image = models.ImageField(upload_to='products/',null=True,blank=True, max_length=225)
    mrp_price = models.IntegerField()
    discount_price = models.IntegerField()
    shape = models.CharField(max_length=12, choices=SHAPE_CHOICES, default='oval', null=True, blank=True)
    website_url = models.URLField(null=True,blank=True)
    users = models.ManyToManyField(User,blank=True)
    created_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "product"

    def __str__(self):
        return self.title
    
class SubscriptionPlanCategory(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        db_table = "subscription_plan_category"


class SubscriptionPlans(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    plan_category = models.ForeignKey(SubscriptionPlanCategory,on_delete=models.CASCADE,null=True,blank=True)
    product = models.ManyToManyField(Product)
    sp_price = models.IntegerField()
    start_date = models.DateField(auto_now_add=False,null=True,blank=True)
    expired_date = models.DateField(auto_now_add=False,null=True,blank=True)
    mode_of_payment = models.PositiveIntegerField(default=STRIPE,choices=PAYMENT_MODES,null=True,blank=True)
    subscription_plan_type = models.PositiveIntegerField(default=BASIC_PLAN,choices=SUBSCRIPTION_PLAN,null=True,blank=True)
    paymod = models.PositiveIntegerField(default=PREPAID,choices=PAYMOD,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True, blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True, blank=True)

    class Meta:
        db_table = "subscription_plans"


    
class Device(models.Model):
    created_by = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)
    device_type = models.PositiveIntegerField(choices=DEVICE_TYPE,null=True,blank=True)
    device_name = models.CharField(max_length=500,null=True,blank=True)
    device_token = models.CharField(max_length=500,null=True,blank=True)
    
    class Meta:
        managed = True
        db_table = 'tbl_device'

    def __str__(self):
        return str(self.device_name)


class Transactions(models.Model):
    amount = models.CharField(max_length=255,default=0,blank=True,null=True)
    currency = models.CharField(max_length=255,default=0,blank=True,null=True)
    receipt_url = models.TextField()
    transaction_id = models.CharField(max_length=255,default=0,blank=True,null=True)
    payment_status = models.CharField(max_length=255,default=0,blank=True,null=True)
    created_on = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="payment_created_by")
    subscription = models.ForeignKey(SubscriptionPlans,on_delete=models.CASCADE,null=True,blank=True)
    payment_type = models.PositiveIntegerField(choices=PAYMENT_TYPE, default=PAYMENT, null=True, blank=True)
    class Meta:
        managed =True
        db_table = 'tbl_transaction'


#### eye test model #######

class Question(models.Model):
    question_text = models.CharField(max_length=255, null=True, blank=True)

    def __str__(self):
        return f"Question - {self.question_text}"
    class Meta:
        db_table = 'question'
    

class EyeTest(models.Model):
    test_of_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="test_of_user")
    selected_question = models.ManyToManyField(Question, blank=True)
    eye_status = models.CharField(max_length=5, choices=EYE_CHOICES, default='left')

    test = models.CharField(max_length=10, null=True, blank=True, choices=VISION_TEST_CHOICES, default='myopia')
    choose_astigmatism = models.CharField(max_length=10,null=True, blank=True, choices=CHOOSE_ASTIGMATISM, default='A')
    degree = models.CharField(max_length=20, null=True, blank=True)

    myopia_snellen_fraction = models.CharField(max_length=20, null=True, blank=True)
    hyperopia_snellen_fraction = models.CharField(max_length=20, null=True, blank=True)
    myopia_sph_power = models.CharField(max_length=20, null=True, blank=True)
    hyperopia_sph_power = models.CharField(max_length=20, null=True, blank=True)

    cyl_text_size = models.CharField(max_length=20, null=True, blank=True)
    cyl_power = models.CharField(max_length=20,null=True, blank=True)
    age_power = models.CharField(max_length=20, null=True, blank=True)
    reading_test_snellen_fraction = models.CharField(max_length=20, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    test_created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f'{self.test_of_user.username} - {self.eye_status} - {self.test}'
    
    class Meta:
        db_table = 'eye_test'

 
class NumberOfLetterInText(models.Model):
    number_of_letter = models.CharField(max_length=10, null=True, blank=True, choices=NUMBER_OF_LETTER, default='two')
    text = models.CharField(max_length=20, null=True, blank=True)
    used = models.BooleanField(default=False)
   
 
    def __str__(self):
        return f"{self.number_of_letter} - {self.used} - {self.text}"
   
    class Meta:
        db_table = 'number_of_letter'
 
class SnellenFraction(models.Model):
    test = models.CharField(max_length=10, null=True, blank=True, choices=SNELLEN_FRACTION_FOR_TEST)
    snellen_fraction = models.CharField(max_length=100, null=True, blank=True)
    power = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    left_action = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
    right_action = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
 
    def __str__(self):
        return f"Snellen-Fraction - {self.snellen_fraction}"
   
    class Meta:
        db_table = 'snellen_fraction'
 
class PowerMapping(models.Model):
    power_mapping = models.CharField(max_length=10, null=True, blank=True, choices=POWER_MAPPING)
    start_range = models.DecimalField(max_digits=7, decimal_places=4,null=True, blank=True)
    end_range = models.DecimalField(max_digits=7, decimal_places=4,null=True, blank=True)
    power = models.DecimalField(max_digits=7, decimal_places=4, null=True, blank=True)
 
    def __str__(self):
        return f"Power-Mapping - {self.power_mapping} - {self.start_range} - {self.power}"
   
    class Meta:
        db_table = 'power_mapping'
       


class Banners(models.Model):
    title = models.CharField(max_length=255,null=True,blank=True)
    description = models.TextField(null=True,blank=True)
    image = models.FileField(upload_to="banner_image",null=True,blank=True)
    created_by = models.ForeignKey(CompanyInformation,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)
    updated_on = models.DateTimeField(auto_now=True,null=True,blank=True)

    class Meta:
        db_table = "tbl_banners"


class ReportReply(models.Model):
    report = models.ForeignKey(ReportIssue,on_delete=models.CASCADE,null=True,blank=True)
    reply = models.TextField(null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    
    class Meta:
        db_table = "tbl_report_reply"

class SpeachText(models.Model):
    text = models.TextField(null=True,blank=True)
    text_language = models.PositiveIntegerField(default=ENGLISH,choices = LANGUAGE_PREFERENCES ,null =True,blank=True)
    page = models.CharField(max_length=200,null=True,blank=True)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    
    class Meta:
        db_table = "tbl_speach_text"

class Logo(models.Model):
    logo_text = models.CharField(max_length=255,null=True,blank=True)
    clients = models.ForeignKey(User,on_delete=models.DO_NOTHING,null=True,blank=True,related_name="clients")
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True,related_name="client_created_by")
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)

    class Meta:
        db_table = "tbl_logo"




class SunglassShapes(models.Model):
    shapes = models.PositiveIntegerField(choices=SUNGLASS_OPTIONS,null=True,blank=True)
    website_url = models.URLField(null=True,blank=True)
    option1 = models.ImageField(upload_to="singlass_options",null=True,blank=True, max_length=225)
    option2 = models.ImageField(upload_to="singlass_options",null=True,blank=True, max_length=225)
    option3 = models.ImageField(upload_to="singlass_options",null=True,blank=True, max_length=225)
    option4 = models.ImageField(upload_to="singlass_options",null=True,blank=True, max_length=225)
    created_by = models.ForeignKey(User,on_delete=models.CASCADE,null=True,blank=True, max_length=225)
    created_on = models.DateTimeField(auto_now_add=True,null=True,blank=True)


    class Meta:
        db_table = "tbl_sunglass_shapes"
