
from django.urls import re_path
from .views import *

urlpatterns = [
        re_path(r'^client-signup-using-mail/$',ClientSignupUsingMail.as_view(),name="client_signup_using_mail"),
        re_path(r'^product-details/$',ProductDetails.as_view(),name="product_details"),
        re_path(r'^product-plans/$',ProductPlans.as_view(),name="product_plans"),
        re_path(r'^product-list/$',ProductsList.as_view(),name="products_list"),

        ##Domain List
        re_path(r'^domain-list/$',DomainList.as_view(),name="domain_list"),
        ##AssignProduct
        re_path(r'^assign-product/$',AssignProduct.as_view(),name="assign_product"),

        ### ClientUserDomainList
        #re_path(r'^client-user-domain-list/$',Client_User_DomainList.as_view(),name="Client_User_DomainList"),

        ##Banners
        re_path(r'^add-banner/$',AddBanner.as_view(),name="add_banner"),
        re_path(r'^banner-list/$',BannerList.as_view(),name="banner_list"),
        re_path(r'^banner-details/$',BannerDetails.as_view(),name="banner_details"),
        re_path(r'^update-banner-details/$',UpdateBanner.as_view(),name="update_banner_details"),

        ## Eyetest data
        
        re_path(r'^eye-test-data/$',EyeTestData.as_view(),name="eye_test_data"),
        re_path(r'^eye-test-data-details/$',EyeTestDataDetails.as_view(),name="eye_test_data_details"),




]