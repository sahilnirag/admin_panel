from api.views import *
from tenant_schemas.utils import get_tenant_model, schema_context
import uuid
class ClientSignupUsingMail(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, *args, **kwargs):
        try:
            company_name = request.data.get('company_name')
            official_number = request.data.get('official_number')
            name_of_person = request.data.get('name_of_person')
            official_domain_email = request.data.get('official_domain_email')
            password = request.data.get('password') 
            sub_domain = request.data.get('sub_domain')

            if not company_name or not official_number or not name_of_person or not password or not sub_domain:
                return Response({"message": "Please fill in all required fields", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            if CompanyInformation.objects.filter(domain_url=sub_domain):
                return Response({"message": "There is already a registered user with this sub domain", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            if CompanyInformation.objects.filter(official_domain_email=official_domain_email):
                return Response({"message": "There is already a registered company with this email", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

            if CompanyInformation.objects.filter(official_number=official_number):
                return Response({"message": "There is already a registered user with this number", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
            
            if CompanyInformation.objects.filter(domain_url=f'{company_name}').exists():
                return Response({"error": f"Domain '{company_name}' already exists."}, status=status.HTTP_400_BAD_REQUEST)

            # Create a new user
            user = User.objects.create(  
                email=official_domain_email,
                password=make_password(password),
                role_id=COMPANY  # Assuming COMPANY is a constant for company role
            )

            domain_url = CompanyInformation.objects.filter(schema_name='public').first().domain_url

            # Create the CompanyInformation object (tenant)
            tenant = CompanyInformation.objects.create(
                company_name=company_name,
                official_number=official_number,
                domain_url=f'{sub_domain}.{domain_url}',
                schema_name=sub_domain, 
                name_of_person=name_of_person,
                official_domain_email=official_domain_email,
                company_uid=uuid.uuid4()
            )
            # Update user fields
            user.full_name = tenant.company_name
            user.first_name = name_of_person
            user.company = tenant
            user.save()
            with schema_context(tenant.schema_name):
                tenant.save()
                user.company = tenant
                user.save()
                tenant.created_by = user
                tenant.save()
            tenant.created_by = user
            tenant.save()
            public_questions = list(Question.objects.all().values())
            with schema_context(tenant.schema_name):
                new_questions = [Question(**data) for data in public_questions]
                Question.objects.bulk_create(new_questions)
            sub_domain = tenant.domain_url
            # Send a confirmation email
            email = official_domain_email
            body = f'Hi,\n\nThank you for contacting us. Here are your login credentials:\nEmail: {email}\nPassword: {password} \nSub Domain:{sub_domain}'
            data = {
                'subject': 'Client Registration',
                'body': body,
                'to_email': email,
            }
            Util.send_email(data)
            return Response({"message": "Signup successful. Please check your email.", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({"message": str(e), "status": status.HTTP_500_INTERNAL_SERVER_ERROR}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        


class ProductsList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self,request,*args,**kwargs):
        products = Product.objects.filter(users=request.user.id).order_by("-created_on")
        Response({"message": "No product found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        data = ProductSerializer(products,context = {"request":request},many=True).data
        return Response({"data":data,"status":status.HTTP_200_OK},status.HTTP_200_OK)
    
class ProductDetails(APIView):
    permission_classes = [permissions.IsAuthenticated,IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({"message": "product_id not provided in the URL query parameters"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            product_details = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            return Response({"message": "No product found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        data = ProductSerializer(product_details, context={"request": request}).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status.HTTP_200_OK)
    

class ProductPlans(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]

    def get(self, request, *args, **kwargs):
        product_id = request.query_params.get('product_id')
        if not product_id:
            return Response({"message": "product_id not provided in the URL query parameters"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            product_details = Product.objects.get(id=product_id)
            plans = product_details.subscriptionplans_set.all()
        except Product.DoesNotExist:
            return Response({"message": "No product found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)

        data = SubscriptionPlanSerializer(plans, context={"request": request}, many=True).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

class DomainList(APIView):
    permission_classes = [permissions.AllowAny]
    parser_classes = [MultiPartParser, JSONParser]

    def post(self, request, *args, **kwargs):
        customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
        provided_token = request.META.get('HTTP_AUTHORIZATION')
        if not provided_token:
            return Response({"error": "Authentication credentials were not provided."}, status=401)
        if provided_token != customer_auth_token:
            return Response({"error": "Invalid token"}, status=401)

        # Get the email from the request data
        email = request.data.get('email')
        if not email:
            return Response({"error": "Email is required"}, status=400)

        try:
            # Try to retrieve the domain URL associated with the provided email
            company_info = CompanyInformation.objects.exclude(schema_name="public").get(official_domain_email=email)
            domain_url = company_info.domain_url
            return Response({"data": domain_url, "status": status.HTTP_200_OK})
        except CompanyInformation.DoesNotExist:
            return Response({"error": "Data not found"}, status=404)
    
class AssignProduct(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def post(self,request,*args,**kwargs):
        user_list =  request.data.get("users",[])
        try:
            product = Product.objects.get(id = request.data.get("product_id"))
        except:
            return Response({"message": "Product not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if not user_list:
            return Response({"message": "Please select users", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        users = User.objects.filter(id__in=user_list)
        for user in users:
            product.users.add(user)
            product.save()
        return Response({"message": "Product assigned successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    

# class Client_User_DomainList(APIView):
#     permission_classes = [permissions.AllowAny]
#     parser_classes = [MultiPartParser, JSONParser]

#     def get(self, request, *args, **kwargs):
#         customer_auth_token = config('CUSTOMER_AUTH_TOKEN')
#         provided_token = request.META.get('HTTP_AUTHORIZATION')
#         if not provided_token:
#             return Response({"error": "Authentication credentials were not provided."}, status=401)
#         if provided_token != customer_auth_token:
#             return Response({"error": "Invalid token"}, status=401)
        
#         domain_url = request.query_params.get('domain_url')
#         if domain_url is None:
#             return Response({"error": "Url parameter is missing"}, status=status.HTTP_400_BAD_REQUEST)
#         try:
#             # Try to retrieve the domain URL associated with the provided id
#             company_info = CompanyInformation.objects.exclude(schema_name="public").get(domain_url=domain_url)
#             domain_url = company_info.domain_url
#             return Response({"data": domain_url, "status": status.HTTP_200_OK})
#         except (ValueError, CompanyInformation.DoesNotExist):
#             return Response({"error": "Data not found"}, status=status.HTTP_404_NOT_FOUND)


class AddBanner(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    
    def post(self,request,*args,**kwargs):
        if Banners.objects.filter(title = request.data.get("title"),created_by = request.user).only("id"):
            return Response({"error": "Banner already added please choose another title"}, status=status.HTTP_404_NOT_FOUND)
        banner = Banners.objects.create(
            title= request.data.get("title"),
            description = request.data.get("description"),
            image = request.FILES.get('image'),
            created_by = request.user
        )
        return Response({"message": "Banner added successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

class BannerList(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self,request,*args,**kwargs):
        banners = Banners.objects.filter(created_by = request.user).order_by("-creayed_on").only("id")
        data = Bannerserializer(banners,many=True).data    
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)
    
class BannerDetails(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self,request,*args,**kwargs):
        banner = Banners.objects.get(id = request.query_params.get("banner_id"))
        data = Bannerserializer(banner).data    
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

class UpdateBanner(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def patch(self,request,*args,**kwargs):
        try:
            banner = Banners.objects.get(id = request.data.get("banner_id"))
        except:
            return Response({"message": "Banner not found", "status": status.HTTP_400_BAD_REQUEST}, status=status.HTTP_400_BAD_REQUEST)
        if request.data.get('title'):
            banner.title = request.data.get("title")
        if request.data.get('description'):
            banner.description = request.data.get("description")
        if request.FILES.get('image'):
            banner.image = request.FILES.get("image")
        banner.save()
        data = Bannerserializer(banner).data    
        return Response({"data": data,"message":"Banner updated successfully", "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)



class EyeTestData(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self, request, *args, **kwargs):
        datetime_str = '2023-11-17 13:00:00'
        datetime_object = datetime.strptime(datetime_str, '%Y-%m-%d %H:%M:%S')

        eye_test = EyeTest.objects.filter(
            Q(test_created_at__date__gte=datetime_object.date()) |
            (Q(test_created_at__date=datetime_object.date()) & Q(test_created_at__time__gte=datetime_object.time()))
        ).only("id").order_by("-test_created_at")
        data = EyeTestSerializer(eye_test, many=True).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)

class EyeTestDataDetails(APIView):
    permission_classes = [permissions.IsAuthenticated,IsClientOrReadOnly]
    parser_classes = [MultiPartParser, JSONParser]
    def get(self,request,*args,**kwargs):
        eye_test = EyeTest.objects.filter(id = request.query_params.get('id')).last()
        data = EyeTestSerializer(eye_test,context={"request":request}).data
        return Response({"data": data, "status": status.HTTP_200_OK}, status=status.HTTP_200_OK)







