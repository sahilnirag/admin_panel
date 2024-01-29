from api.models import *
from rest_framework import serializers as Serializers
from rest_framework.authtoken.models import Token
from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from api.utils import Util
from decouple import config
from django.utils.encoding import smart_str, force_bytes, DjangoUnicodeDecodeError
from django_db_logger.models import StatusLog

class UserSerializer(Serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','full_name','first_name','last_name','email','mobile_no','profile_pic','address','city','state','country','role_id','status','company','full_name','age','face_shape']

class CompanySerializer(Serializers.ModelSerializer):
    created_by = Serializers.SerializerMethodField(read_only=True)
    created_by_id = Serializers.SerializerMethodField(read_only=True)

    def get_created_by(self, obj):
        return obj.created_by.full_name if obj.created_by.full_name else obj.created_by.email

    def get_created_by_id(self, obj):
        return obj.created_by.id

    class Meta:
        model = CompanyInformation
        fields = "__all__"

class ProductSerializer(Serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'

class PlanCategorySerializer(Serializers.ModelSerializer):
    class Meta:
        model = SubscriptionPlanCategory
        fields = '__all__'

class SubscriptionPlanSerializer(Serializers.ModelSerializer):
    plan_category = Serializers.SerializerMethodField(read_only=True)
    created_by = Serializers.SerializerMethodField(read_only =True)
    plan_validity = Serializers.SerializerMethodField(read_only =True)

    def get_plan_category(self,obj):
        return obj.plan_category.title
    
    def get_created_by(self,obj):
        return obj.created_by.full_name if obj.created_by.full_name else obj.created_by.email
    
    def get_plan_validity(self,obj):
        return  (obj.expired_date-obj.start_date).days

    class Meta:
        model = SubscriptionPlans
        fields = ['id',"title","description","plan_category","sp_price","product","subscription_plan_type","paymod","start_date","expired_date","created_by","plan_validity"]


class NotificationSerializer(Serializers.ModelSerializer):
    image = Serializers.SerializerMethodField(read_only=True)
    created_by = Serializers.SerializerMethodField(read_only=True)

    def get_image(self,obj):
        request = self.context.get('request')
        return request.build_absolute_uri(obj.image.url)
       
    def get_created_by(self,obj):
        return obj.created_by.full_name if obj.created_by.full_name else obj.created_by.email
       

    class Meta:
        model = Notification
        fields = ['id','title','description','created_by','image']


class SendPasswordResetEmailSerializer(Serializers.Serializer):
        email = Serializers.EmailField(max_length=255)
        class Meta:
            fields = ['email']

        def validate(self, attrs):
            email = attrs.get('email')
            if User.objects.filter(email=email).exists():
                user = User.objects.get(email = email)
                if user.role_id != COMPANY:
                  raise Serializers.ValidationError('You do not have permission to perform this action.')
                uid = urlsafe_base64_encode(force_bytes(user.id))
                token = PasswordResetTokenGenerator().make_token(user)
                FRONTEND_URL = config('FRONTEND_URL')
                link = f'{FRONTEND_URL}/auth/reset-password/{uid}/{token}/'
                body = f'Click Following Link to Reset Your Password {link}'
                data = {
                    'subject':'Reset Your Password',
                    'body':body,
                    'to_email':user.email
                }
                Util.send_email(data)
                return attrs
            else:
                raise Serializers.ValidationError('You are not a Registered User')


class UserPasswordResetSerializer(Serializers.Serializer):
    password = Serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    password2 = Serializers.CharField(max_length=255, style={'input_type':'password'}, write_only=True)
    class Meta:
        fields = ['password', 'password2']

    def validate(self, attrs):
        try:
            password = attrs.get('password')
            password2 = attrs.get('password2')
            uid = self.context.get('uid')
            token = self.context.get('token')
            if password != password2:
                raise Serializers.ValidationError("Password and Confirm Password doesn't match")
            id = smart_str(urlsafe_base64_decode(uid))
            user = User.objects.get(id=id)
            if not PasswordResetTokenGenerator().check_token(user, token):
                raise Serializers.ValidationError('Token is not Valid or Expired')
            user.set_password(password)
            user.save()
            return attrs
        except DjangoUnicodeDecodeError as identifier:
            PasswordResetTokenGenerator().check_token(user, token)
            raise Serializers.ValidationError('Token is not Valid or Expired')


class LogsSerializer(Serializers.ModelSerializer):
    class Meta:
        model = StatusLog
        fields = '__all__'

class ReportSerializer(Serializers.ModelSerializer):
    created_by = Serializers.SerializerMethodField(read_only=True)

    def get_created_by(self, obj):
        return obj.created_by.full_name if obj.created_by.full_name else obj.created_by.email
    class Meta:
        model = ReportIssue
        fields = '__all__'

class TransactionSerializer(Serializers.ModelSerializer):
    created_by = Serializers.SerializerMethodField(read_only=True)
    subscription = Serializers.SerializerMethodField(read_only=True)
           
    def get_created_by(self,obj):
        return obj.created_by.full_name if obj.created_by.full_name else obj.created_by.email
    def get_subscription(self,obj):
        return obj.subscription.title if obj.subscription.title else ""
    
    class Meta:
        model = Transactions
        fields = '__all__'



class CustomerRecordSerializer(Serializers.Serializer):
    domain_url = Serializers.CharField()
    name = Serializers.CharField()
    age = Serializers.IntegerField()



class PaymentIntentSerializer(Serializers.Serializer):
    amount = Serializers.IntegerField(required=True)
    name = Serializers.CharField(max_length=100, required=True)
    email = Serializers.EmailField(required=True)
    address = Serializers.CharField(max_length=200, required=True)



####### eyetest #############

class EyeTestSerializer(Serializers.ModelSerializer):
    full_name = Serializers.SerializerMethodField(read_only=True)
    mobile = Serializers.SerializerMethodField(read_only=True)
    feedback = Serializers.SerializerMethodField(read_only=True)
    face_shape = Serializers.SerializerMethodField(read_only=True)
    
    def get_full_name(self,obj):
        return obj.test_of_user.full_name if obj.test_of_user.full_name else None
    
    def get_mobile(self,obj):
        return obj.test_of_user.mobile_no if obj.test_of_user.mobile_no else None
    
    def get_feedback(self,obj):
        return obj.test_of_user.user_feedback if obj.test_of_user.user_feedback else None
    
    def get_face_shape(self,obj):
        return obj.test_of_user.face_shape if obj.test_of_user.face_shape else None
    
    class Meta:
        model = EyeTest
        fields = '__all__'
 
class QuestionSerializer(Serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = '__all__'
 
class NumberOfLetterInTextSerializer(Serializers.ModelSerializer):
    class Meta:
        model = NumberOfLetterInText
        fields = '__all__'
 
class SnellenFractionSizeSerializer(Serializers.ModelSerializer):
    class Meta:
        model = SnellenFraction
        fields = ['snellen_fraction']
 
class PowerMappingSerializer(Serializers.ModelSerializer):
    class Meta:
        model = PowerMapping
        fields = '__all__'

class Bannerserializer(Serializers.ModelSerializer):
    class Meta:
        models = Banners
        fields = "__all__"


class DisplayRandomTextSerializer(Serializers.Serializer):
    test_id = Serializers.IntegerField( required=True)
    action = Serializers.CharField(max_length=255, required=True)
    vision_test = Serializers.CharField(max_length=255, required=False)
    snellen_fraction = Serializers.CharField(max_length=255, required=True)
 
    class Meta:
        fields = ['test_id','action', 'snellen_fraction','vision_test']

class ReadingTestSerializer(Serializers.Serializer):
    test_id = Serializers.IntegerField(required=True)
    snellen_fraction = Serializers.CharField(max_length=100, required=True)
 
    class Meta:
        fields = ['test_id','snellen_fraction']


class SpeachTextSerializer(Serializers.ModelSerializer):
    class Meta:
        model = SpeachText
        fields = '__all__'

class LogoSerializer(Serializers.ModelSerializer):
       clients = Serializers.SerializerMethodField(read_only=True)
       def get_clients(self, obj):
            return obj.clients.full_name if obj.clients.full_name else obj.clients.email
       class Meta:
        model = Logo
        fields = ['id','logo_text', 'clients','created_on']



class SunglassShapeSerializer(Serializers.ModelSerializer):
    class Meta:
        model = SunglassShapes
        fields = '__all__'