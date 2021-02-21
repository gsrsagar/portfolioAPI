
from django.urls import include, path
from .views import UserViewSet, GroupViewSet, add_item, register_personal_details, \
    delete_personal_details, get_all_personal_details, register_experience, register_skill, \
    register_education, register_career_objective, register_resume_builder, register_project, get_all_skills, \
    get_all_projects, get_all_education_list, get_all_experiences, get_all_resumes, get_all_career_objectives, \
    get_experience_data, get_education_data, get_skills_data, get_personal_data, get_resume_data, \
    get_career_objective_data, modify_resume_data, modify_skills_data, modify_education_data, modify_experience_data, \
    modify_career_objective_data, modify_personal_data, get_project_data, modify_project_data, delete_project_details, \
    delete_skill_details, delete_education_details, delete_experience_details, delete_career_objective_details, \
    delete_resume_details, RegisterAPI, login, Logout, google_login, change_password, forgot_password, send_otp_key, \
    get_resume_data_by_id, get_personal_data_by_id, register_language_details, register_trainings_certificates_details, \
    register_hobbie_details, get_language_data, get_hobbie_data, get_training_certificates_data, modify_language_data, \
    modify_training_certificates_data, modify_hobbie_data, delete_language_details, delete_hobbie_details, \
    delete_training_certificate_details, generate_otp_sign_up, modify_user
from rest_framework import routers
from knox import views as knox_views
from rest_framework.authtoken import views


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'Groups', GroupViewSet)
urlpatterns = [
    path('api/', include(router.urls)),
    path('api/accounts/', include('allauth.urls')),
    path('api/register/', RegisterAPI.as_view(), name='register'),
    path('api/login/', login, name='login'),
    path('api/google_login/', google_login, name='google_login'),
    path('api/change_password/', change_password, name='change_password'),
    path('api/forgot_password/', forgot_password, name='forgot_password'),
    path('api/get_otp_key/', send_otp_key, name='get_otp_key'),
    path('api/generate_otp_key/', generate_otp_sign_up, name='generate_otp_key'),
    path('api/logout/', Logout, name='logout'),
    path('api/logout_all/', knox_views.LogoutAllView.as_view(), name='logout_all'),
    path('api/add_item/', add_item),
    path('api/register_personal_details/', register_personal_details),
    path('api/modify_user_details/', modify_user),
    path('api/register_experience/', register_experience),
    path('api/register_skill/', register_skill),
    path('api/register_project/', register_project),
    path('api/register_education/', register_education),
    path('api/register_career_objective/', register_career_objective),
    path('api/register_resume_builder/', register_resume_builder),
    path('api/register_language/', register_language_details),
    path('api/register_training_certificates/', register_trainings_certificates_details),
    path('api/register_interest_hobbies/', register_hobbie_details),
    path('api/get_all_personal_details/', get_all_personal_details),
    path('api/get_all_skills/', get_all_skills),
    path('api/get_all_projects/', get_all_projects),
    path('api/get_all_education_list/', get_all_education_list),
    path('api/get_all_experiences/', get_all_experiences),
    path('api/get_all_resumes/', get_all_resumes),
    path('api/get_all_career_objectives/', get_all_career_objectives),
    path('api/get_all_personal_details/', get_all_personal_details),
    path('api/get_experience_data/<int:pk>', get_experience_data),
    path('api/get_education_data/<int:pk>', get_education_data),
    path('api/get_skills_data/<int:pk>', get_skills_data),
    path('api/get_personal_data/<int:pk>', get_personal_data),
    path('api/get_resume_data/<int:pk>', get_resume_data),
    path('api/get_resume_data_by_id/', get_resume_data_by_id),
    path('api/get_career_objective_data/<int:pk>', get_career_objective_data),
    path('api/get_project_data/<int:pk>', get_project_data),
    path('api/get_language_data/<int:pk>', get_language_data),
    path('api/get_hobbies_data/<int:pk>', get_hobbie_data) ,
    path('api/get_training_data/<int:pk>', get_training_certificates_data),
    path('api/get_personal_data_by_id/', get_personal_data_by_id),
    path('api/modify_resume_details/<int:pk>', modify_resume_data),
    path('api/modify_skills_details/<int:pk>', modify_skills_data),
    path('api/modify_education_details/<int:pk>', modify_education_data),
    path('api/modify_experience_details/<int:pk>', modify_experience_data),
    path('api/modify_career_objective_details/<int:pk>', modify_career_objective_data),
    path('api/modify_personal_details/<int:pk>', modify_personal_data),
    path('api/modify_project_details/<int:pk>', modify_project_data),
    path('api/modify_language_details/<int:pk>', modify_language_data),
    path('api/modify_training_details/<int:pk>', modify_training_certificates_data),
    path('api/modify_hobbies_details/<int:pk>', modify_hobbie_data),
    path('api/delete_personal_details/', delete_personal_details),
    path('api/delete_project_details/', delete_project_details),
    path('api/delete_skill_details/', delete_skill_details),
    path('api/delete_education_details/', delete_education_details),
    path('api/delete_experience_details/', delete_experience_details),
    path('api/delete_career_objective_details/', delete_career_objective_details),
    path('api/delete_resume_details/', delete_resume_details),
    path('api/delete_language_details/', delete_language_details),
    path('api/delete_hobbies_details/', delete_hobbie_details),
    path('api/delete_training_details/', delete_training_certificate_details)


]
