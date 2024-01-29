from api.models import *
from rest_framework.views import APIView 
from api.serializer import *
from rest_framework.parsers import MultiPartParser,JSONParser
from rest_framework.exceptions import PermissionDenied
from rest_framework import  permissions,status,viewsets
from rest_framework.response import Response 
from django.contrib.auth.hashers import make_password
from rest_framework import  permissions,status,viewsets,generics,filters
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import  Q
from tenant_schemas.utils import get_tenant_model, schema_context
from api.views import IsAdminOrReadOnly,IsClientOrReadOnly,IsCustomerOrReadOnly
from api.pagiation import *
import stripe
stripe.api_key = config("STRIPE_KEY")



class ClietsListig(APIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        clients = CompanyInformation.objects.filter(created_by__role_id=COMPANY).order_by("-created_on")
        if request.query_params.get("search_user"):
            clients = clients.filter(name_of_person__icontains =  request.query_params.get("search_user"))
        start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,clients )
        data = CompanySerializer(clients[start:end],many =True).data
        return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)

 

class UpdateClientProfile(APIView):
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser,JSONParser]
    def put(self,request, client_id, *args, **kwargs):
        try:
            comapany = CompanyInformation.objects.get(id =client_id)
        except:
            return Response({"message":"Client not found","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        if CompanyInformation.objects.filter(official_number = request.data.get('official_number')).exclude(id = client_id):
            return Response({"message":"There is already a registered company with this number","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        if CompanyInformation.objects.filter(company_name = request.data.get('company_name')).exclude(id = client_id):
            return Response({"message":"There is already a registered company with this name","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        if CompanyInformation.objects.filter(official_website__isnull=False, official_website = request.data.get('official_website')).exclude(id = client_id):
            return Response({"message":"There is already a registered company with this website","status":status.HTTP_400_BAD_REQUEST},status.HTTP_400_BAD_REQUEST)
        if request.data.get("company_name"):
            comapany.company_name = request.data.get("company_name")
        if request.data.get("official_number"):
            comapany.official_number= request.data.get("official_number")
        if request.data.get("company_address"):
            comapany.company_address = request.data.get("company_address")
        if request.data.get("city"):
            comapany.city = request.data.get("city")
        if request.data.get("state"):
            comapany.state = request.data.get("state")
        if request.data.get("country"):
            comapany.country = request.data.get("country")
        if request.data.get("official_website"):
            comapany.official_website = request.data.get("official_website")
        if request.data.get("name_of_person"):
            comapany.name_of_person = request.data.get("name_of_person")
        if request.data.get("daily_business"):
            comapany.daily_business = request.data.get("daily_business")
        comapany.save()
        with schema_context(comapany.schema_name):
            comapany.save()
        return Response({"message":"Profile updated successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)



class ClientInformationListView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated, IsAdminOrReadOnly]
    queryset = CompanyInformation.objects.all()
    serializer_class = CompanySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = {
        # Add filter fields here if needed
    }

    def get_queryset(self):
        # Get the search term from the request's query parameters
        search_term = self.request.query_params.get('search', '')

        # Define the fields you want to search
        search_fields = [
            'company_name',
            'official_number',
            'city',
            'state',
            'country',
            'official_website',
            'official_domain_email',
            'business_id',
            'requirement',
            'name_of_person',
            'designation',
            'daily_business',
            'created_by__email'  # Assuming created_by is a ForeignKey to User model
        ]

        # Create a dynamic OR query using Q objects for each field with icontains
        query = Q()
        for field in search_fields:
            query |= Q(**{f"{field}__icontains": search_term})

        # Apply the query to the queryset
        return self.queryset.filter(query)

class AddSunglassOptions(APIView):
    permission_classes = [permissions.IsAuthenticated,IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        if not request.data.get("shapes"):
            return Response({"message":"Please select shapes","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("website_url"):
            return Response({"message":"Please enter website url","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.FILES.get("option1"):
            return Response({"message":"Please select option1","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option1price"):
            return Response({"message":"Please enter price for option 1","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option1discountprice"):
            return Response({"message":"Please enter discount price for option 1","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.FILES.get("option2"):
            return Response({"message":"Please select option2","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option2price"):
            return Response({"message":"Please enter price for option 2","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option2discountprice"):
            return Response({"message":"Please enter discount price for option 2","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.FILES.get("option3"):
            return Response({"message":"Please select option3","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option3price"):
            return Response({"message":"Please enter price for option 3","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option3discountprice"):
            return Response({"message":"Please enter discount price for option 3","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.FILES.get("option4"):
            return Response({"message":"Please select option4","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option4price"):
            return Response({"message":"Please enter price for option 4","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if not request.data.get("option4discountprice"):
            return Response({"message":"Please enter discount price for option 4","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)

        SunglassShapes.objects.create(
            shapes= request.data.get("shapes"),
            website_url = request.data.get("website_url"),

            option1 = request.FILES.get("option1"),
            option1price = request.data.get("option1price"),
            option1discountprice = request.data.get('option1discountprice'),

            option2 = request.FILES.get("option2"),
            option2price = request.data.get("option2price"),
            option2discountprice = request.data.get('option2discountprice'),

            option3 = request.FILES.get("option3"),
            option3price = request.data.get("option3price"),
            option3discountprice = request.data.get('option3discountprice'),

            option4 = request.FILES.get("option4"),
            option4price = request.data.get("option4price"),
            option4discountprice = request.data.get('option4discountprice'),

            created_by = request.user
            )  
        return Response({"message":"Sunglass options added successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class UpdateSunglassOptions(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def post(self,request,*args,**kwargs):
        try:
            shapes =SunglassShapes.objects.get(id = request.data.get("id"))
        except:
            return Response({"message":"Invalid data","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        if request.data.get("shapes"):
            shapes.shapes = request.data.get("shapes")
            
        if request.data.get("website_url"):
            shapes.website_url = request.data.get("website_url")
            
        if request.FILES.get("option1"):
            shapes.option1 = request.FILES.get("option1")
        if request.data.get("option1price"):
            shapes.option1price = request.data.get("option1price")
        if request.data.get("option1discountprice"):
            shapes.option1discountprice = request.data.get("option1discountprice")
            
        if request.FILES.get("option2"):
            shapes.option2 = request.FILES.get("option2")
        if request.data.get("option2price"):
            shapes.option2price = request.data.get("option2price")
        if request.data.get("option2discountprice"):
            shapes.option2discountprice = request.data.get("option2discountprice")
            
        if request.FILES.get("option3"):
            shapes.option3 = request.FILES.get("option3")
        if request.data.get("option3price"):
            shapes.option3price = request.data.get("option3price")
        if request.data.get("option3discountprice"):
            shapes.option3discountprice = request.data.get("option3discountprice")
            
        if request.FILES.get("option4"):
            shapes.option4 = request.FILES.get("option4")
        if request.data.get("option4price"):
            shapes.option4price = request.data.get("option4price")
        if request.data.get("option4discountprice"):
            shapes.option4discountprice = request.data.get("option4discountprice")
        
        shapes.save()
        return Response({"message":"Sunglass options updated successfully","status":status.HTTP_200_OK},status=status.HTTP_200_OK)


class SunglassListForclients(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]

    def get(self, request):
            shapes=SunglassShapes.objects.filter(created_by = request.user).order_by("-created_on")
            start,end,meta_data = GetPagesData(request.query_params.get("page") if request.query_params.get("page") else None,shapes )
            data = SunglassShapeSerializer(shapes[start:end], context = {"request":request},many =True).data 
            return Response({"data":data,"meta":meta_data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    

class GetSunglassForclients(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]

    def get(self,request,*args,**kwargs):
        try:
            text = SunglassShapes.objects.get(id =request.query_params.get("id"))
        except:
            return Response({"message":"Invalid data","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        data = SunglassShapeSerializer(text,context={"request":request}).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)
    
class DeleteSunglassForclients(APIView):
    permission_classes = [permissions.IsAuthenticated, IsClientOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def delete(self,request,*args,**kwargs):
        try:
            shapes = SunglassShapes.objects.get(id = request.query_params.get('id'))
        except:
             return Response({"message":"shapes does not exist","status":status.HTTP_400_BAD_REQUEST},status=status.HTTP_400_BAD_REQUEST)
        shapes.delete()
        return Response({"message":"glass-shapes deleted Successfully","status":status.HTTP_200_OK},status.HTTP_200_OK)
            


class ShapesDetailsForUser(APIView):
    permission_classes = [permissions.IsAuthenticated,IsCustomerOrReadOnly]
    parser_classes = [MultiPartParser,JSONParser]
    def get(self,request,*args,**kwargs):
        shapes = Product.objects.filter(shape = request.query_params.get('shape'))[:4]       
        data = ProductSerializer(shapes,context={"request":request},many=True).data
        return Response({"data":data,"status":status.HTTP_200_OK},status=status.HTTP_200_OK)


