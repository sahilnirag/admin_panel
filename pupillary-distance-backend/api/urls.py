from django.urls import path,include
from .views import *
from .views_client import *
from django.urls import re_path
from rest_framework.routers import DefaultRouter
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static
from .views_eyetest import *
from .camera import CalculateDistance
#from .views_eyetest import EyeTestViewSet
app_name='api'



router = DefaultRouter()
router.register(r'products', ProductViewSet)
#router.register(r'eye-tests', EyeTestViewSet)

urlpatterns = [

    ##Authentication
    re_path(r'^client-detail-get/$',ClientInformationListView.as_view(),name="ClientInformationListView"),
    re_path(r'^customer-signup/$',CustomerSignup.as_view(),name="customer_signup"),
    re_path(r'^user-list-search/$',UserInformationListView.as_view(),name="UserInformationListView"),
    re_path(r'^add-customer/$',AddCustomer.as_view(),name="add_customer"),
    re_path(r'^login/$',Login.as_view(),name="login"),
    re_path(r'^logout/$',LogOut.as_view(),name="logout"),
    re_path(r'^change-password/$',ChangePassword.as_view(),name="change_password"),
 
    ##Update Admin Profiele
    re_path(r'^update-admin-profile/$',UpdateAdminProfile.as_view(),name="update_admin_profile"),
    re_path(r'^get-admin-profile/$',GetAdminProfile.as_view(),name="GetAdminProfile"),

    ## Update Client Profile
    
    re_path(r'^update-client-profile/(?P<client_id>[\w-]+)/$',UpdateClientProfile.as_view(),name="update_client_profile"),

    ## Delete USer
    re_path(r'^delete-user-account/$',DeleteUserAccount.as_view(),name="delete_user_account"),
    ##Deactivate User Account
    re_path(r'^deactivate-user-account/$',DeactivateUseraccount.as_view(),name="deactivate_user_account"),


    ## forget password
    re_path(r'^send-reset-password-email/$', SendPasswordResetEmailView.as_view(), name='send-reset-password-email'),
    re_path(r'^reset-password/(?P<uid>[\w-]+)/(?P<token>[\w-]+)/$', UserPasswordResetView.as_view(), name='reset-password'),


    re_path(r'^admin-Dashboard-details/$', AdminDashboarddetails.as_view(), name='AdminDashboarddetails'),

    ##Report Issue
    re_path(r'^add-reportIssue/$',AddReportIssue.as_view(),name="add_report_issue"),
    re_path(r'^delete-reportIssue/$',Deletreports.as_view(),name="delete_report_issue"),
    re_path(r'^report-issues-list/$',ReportList.as_view(),name="report_issues_list"),
    re_path(r'^report-issues-details/$',ReportDetails.as_view(),name="report_details"),
    re_path(r'^send-reply/$',ReplyToReports.as_view(),name="send_reply"),


    ##Notification
    re_path(r'^enable-disable-notification/$',EnableDisableNotification.as_view(),name="enable_disable_notification"),
    re_path(r'^create-notification/$',CreateNotification.as_view(),name="create_notification"),
    re_path(r'^admin-notifications-list/$',AdminNotificationsList.as_view(),name="admin_notifications_list"),
    re_path(r'^delete-notification/$',DeleteNotification.as_view(),name="delete_notification"),
    re_path(r'^update-notification/$',UpdateNotification.as_view(),name="update_notification"),

    ## Plan Category
    re_path(r'^add-plans-categories/$',AddPlansCategories.as_view(),name="add_plans_categories"),
    re_path(r'^update-plans-categories/$',UpdatePlansCategories.as_view(),name="update_plans_categories"),
    re_path(r'^plans-categories-list/$',PlansCategoriesList.as_view(),name="plans_categories_list"),
    re_path(r'^delete-plans-category/$',DeletePlansCategories.as_view(),name="delete_plans_categories"),
    re_path(r'^notification-details/$',NotificationDetails.as_view(),name="notification_etails"),

    ##Subscription Plan
    re_path(r'^add-subscription-plans/$',AddPlans.as_view(),name="add_subscription_plans"),
    re_path(r'^subscription-plans-list/$',PlansList.as_view(),name="subscription_plans_list"),
    re_path(r'^update-subscription-plans/$',UpdatePlan.as_view(),name="update_subscription_plans"),
    re_path(r'^delete-subscription-plans/$',DeleteSubscriptionPlan.as_view(),name="delete_subscription_plan"),
     
    

    ## Transactions
    re_path(r'^transaction-list/$',TransactionList.as_view(),name="transaction_list"),
    re_path(r'^transaction-details/$',TransactionsDetails.as_view(),name="transactions_details"),



    ##Clients
    re_path(r'^clients-listing/$',ClietsListig.as_view(),name="client_listing"),
    re_path(r'^client-details$',ClientListForEnduser.as_view(),name="client_details"),


     re_path(r'^get-subscription-plans-category/(?P<pk>\d+)/$', GetSubscriptionPlanCategoryAPIView.as_view(), name='GetSubscriptionPlanCategoryAPIView'),
     re_path(r'^get-subscription-plans/(?P<pk>\d+)/$', GetSubscriptionPlanAPIView.as_view(), name='GetSubscriptionPlanAPIView'),

    ##
    
    re_path(r'^error-logs-list/$',ErrorLogsList.as_view(),name="error_logs_list"),
    re_path(r'^error-logs-details/$',ErroLogsDetails.as_view(),name="error_logs_details"),
    re_path(r'^delete-error-logs/$',DeleteErrorLogs.as_view(),name="delete_error_logs"),

    ## Checkingtokenexpired ###
    re_path(r'^check-token-expiry/$',CheckTokenExpiry.as_view(),name="CheckTokenExpiry"),

    ### get customer Record
    re_path(r'^get-customer-record/$',GetCustomerRecord.as_view(),name="GetCustomerRecord"),


    #### payment with stripe #####
    re_path(r'^create-payment-intent/$',CreatePaymentIntent.as_view(),name="CreatePaymentIntent"),
    re_path(r'^get-payment-receipt/$',GetPaymentReceiptDetail.as_view(),name="GetPaymentReceiptDetail"),
    re_path(r'^stripe-webhook-intent/$',StripeWebhookView.as_view(),name="StripeWebhookView"),
    re_path(r'^autometic-paymet/$',AutometicPaymet.as_view(),name="autometic_paymet"),

    re_path(r'^get-user-detail/(?P<pk>\d+)/$', GetUserDetailView.as_view(), name='GetUserDetailView'),

    ###client dashboard api
    re_path(r'^client-dashboard-details/$',ClientDashboardDetails.as_view(),name="ClientDashboardDetails"),

    re_path(r'^client-data-get/(?P<client_id>[\w-]+)/$',getClientDetail.as_view(),name="client_signup"),

    ### start eye test url ####
    re_path(r'^select-questions/$', SelectQuestions.as_view(), name="select_questions"),
    re_path(r'^random-text/$', DisplayRandomText.as_view(), name="random_text"),
    re_path(r'^myopia-or-hyperopia-or-presbyopia-test/$', MyopiaOrHyperopiaOrPresbyopiaTestApi.as_view(), name="myopia_or_hyperopia_or_presbyopia_test"),
    re_path(r'^snellen-fraction/$', GetSnellenFractionApi.as_view(), name="myopia_snellen_fraction"),
    re_path(r'^choose-astigmatism/$', ChooseAstigmatism.as_view(), name="choose_astigmatism"),
    re_path(r'^get-degrees/$', GetDegreeApi.as_view(), name="get_degrees"),
    re_path(r'^choose-degree-api/$', ChooseDegreeApi.as_view(), name="choose_degree_api"),
    re_path(r'^cyl-test/$', CYLTestApi.as_view(), name="cyl_test"),
    re_path(r'^genrate-report/$', GetReportData.as_view(), name="genrate_report"),
    re_path(r'^select-eye/$', SelectEye.as_view(), name="SelectEye"),
    re_path(r'^get-question-details/$', ShowQuestion.as_view(), name="ShowQuestion"),
    re_path(r'^insert-constant-data/$', ConstantInsertDataInDB.as_view(), name="ConstantInsertDataInDB"),
    re_path(r'^calculate-distance/$', CalculateDistance.as_view(), name="CalculateDistance"),
    re_path(r'^text-to-speech-api/$', TextToSpeechApi.as_view(), name="TextToSpeechApi"),
    re_path(r'^user-feedback-api/$', UserFeedbackApi.as_view(), name="UserFeedbackApi"),
    re_path(r'^already-selected-eye/$', AllreadySeletedEye.as_view(), name="AllreadySeletedEye"),
    re_path(r'^random-word-test/$', RandomWordTestApi.as_view(), name="RandomWordTestApi"),
    re_path(r'^snellen-fraction-red-green-test/$', GetSnellenFractionForRedGreenTestApi.as_view(), name="GetSnellenFractionForRedGreenTestApi"),
    re_path(r'^final-red-green-action-test/$', FindSnellenFractionAccordingRedAndGreenAction.as_view(), name="FindSnellenFractionAccordingRedAndGreenAction"),
    re_path(r'^update-red-green-action-api/$', UpdateRedAndGreenTestApi.as_view(), name="UpdateRedAndGreenTestApi"),
    re_path(r'^update-Reading-SnellenFraction-TestApi/$', SaveReadingSnellenFractionTestApi.as_view(), name="SaveReadingSnellenFractionTestApi"),
    re_path(r'^counter-api/$', CounterApi.as_view(), name="CounterApi"),

    ## Add speach text
    re_path(r'^speach-text-data/$', SpeachTextdata.as_view(), name="speach_text_data"),
    re_path(r'^speach-text-list-for-admin/$', SpeachTextListForAdmin.as_view(), name="speach_text_list_for_admin"),
    re_path(r'^speach-text-list-for-users/$', SpeachTextListForUser.as_view(), name="speach_text_list_for_users"),
    re_path(r'^speach-text-details-for-admin/$', SpeachTextDetailsForAdmin.as_view(), name="speach_text_details_for_admin"),

    ## Add user preference
    
    re_path(r'^select-laguage-prefrence/$', SelectLaguagePrefrence.as_view(), name="select_laguage_prefrence"),

    ##Add Logo
    re_path(r'^add-client-logo/$', AddLogo.as_view(), name="AddLogo"),
    re_path(r'^list-client-logo/$', LogolistForAdmin.as_view(), name="LogolistForAdmin"),
    re_path(r'^logo-for-client/$', LogoForClient.as_view(), name="LogoForClient"),

    ##re_path(r'^track-user-activity/$', TrackUserActivity.as_view(), name="track_user_activity"),

    re_path(r'^get-client_web_url/$', GetClient_web_url.as_view(), name="GetClient_web_url"),

    ### end eye test url ####

    ## Sunglass Shapes
    
    re_path(r'^add-sunglass-options/$', AddSunglassOptions.as_view(), name="add_sunglass_options"),
    re_path(r'^update-sunglass-options/$', UpdateSunglassOptions.as_view(), name="update_sunglass_options"),
    re_path(r'^sunglass-list-for-clients/$', SunglassListForclients.as_view(), name="sunglass_list_for_clients"),
    re_path(r'^get-sunglass-for-clients/$', GetSunglassForclients.as_view(), name="GetSunglassForclients"),
    re_path(r'^delete-sunglass-for-clients/$', DeleteSunglassForclients.as_view(), name="DeleteSunglassForclients"),
    re_path(r'^shapes-details-for-user/$', ShapesDetailsForUser.as_view(), name="shapes_details_for_user"),
    re_path(r'^client-user-count/$', GetClient_user_count.as_view(), name="GetClient_user_count"),

    ##Pd distance
    re_path(r'^pd-distance-report/$', PdDistanceReport.as_view(), name="pd_distance_report"),




    path('', include(router.urls))

   
    
    

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)