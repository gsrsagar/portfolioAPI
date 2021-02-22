
from django.contrib.auth import authenticate
from django.http import JsonResponse
from django.shortcuts import render
from knox.models import AuthToken
from knox.views import LoginView as KnoxLoginView
import datetime
from django.conf import settings
import random
from django.views.decorators.csrf import csrf_exempt
from rest_framework.authtoken.serializers import AuthTokenSerializer
from rest_framework.decorators import api_view
from rest_framework import viewsets, permissions, generics
from rest_framework.parsers import JSONParser
from rest_framework.response import Response
from rest_framework.status import HTTP_400_BAD_REQUEST, HTTP_404_NOT_FOUND, HTTP_200_OK
from rest_framework.templatetags.rest_framework import data
from rest_framework.views import APIView
from django.core.mail import send_mail

from .models import PersonalDetails, Experience, Project, Skill, Education, ResumeBuilder, CareerObjective, OTPVerify, \
    InterestesHobbies, Languages, TrainingCertificates
from .serializers import ItemSerializer, UserSerializer, GroupSerializer, RegisterSerializer, PersonalDetailsSerializer, \
    SkillSerializer, EducationSerializer, ExperienceSerializer, CareerObjectiveSerializer, ResumeBuilderSerializer, \
    ProjectSerializer, OTPVerifySerializer, InterestsHobbiesSerializer, LanguagesSerializer, TrainingCertificatesSerializer
from rest_framework import status
from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authtoken.models import Token
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.authentication import TokenAuthentication
from django.contrib.auth.models import User, Group

email_Id_developer = "developers.margeylabs@gmail.com"

class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer
    permission_classes = [permissions.IsAuthenticated]


# Register API
class RegisterAPI(generics.GenericAPIView):
    serializer_class = RegisterSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            OTPVerify.objects().filter(email=request.data.get("email")).delete()
        except:
            print("")
        user = serializer.save()
        token, _ = Token.objects.get_or_create(user=user)
        return Response({
        "user": UserSerializer(user, context=self.get_serializer_context()).data,
        "token": token.key
        }, status=status.HTTP_201_CREATED)


# class LoginAPI(KnoxLoginView):
#     permission_classes = (permissions.AllowAny,)
#
#     def post(self, request, format=None):
#         user = User.objects.get(email=request.data.get("email"))
#         email = request.data["email"]
#         password = request.data.get("password")
#         if email is None or password is None:
#             return Response({'error': 'Please provide both username and password'},status=status.HTTP_400_BAD_REQUEST)
#         # serializer = AuthTokenSerializer(data=request.data)
#         # serializer.is_valid(raise_exception=True)
#         # user = serializer.validated_data['user']
#         login(request, user)
#         return Response((super(LoginAPI, self).post(request, format=None)), status=status.HTTP_200_OK)
@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def forgot_password(request):
    email = request.data.get('email')
    otp = request.data.get('otp')
    password = request.data.get('new_password')
    password2 = request.data.get('new_password2')
    user_data = User.objects.get(email=request.data.get("email"))
    otp_data = OTPVerify.objects.filter(otpKey=otp, email=email)
    otp_data.isVerified =True
    OTPVerify.objects().filter(email=email).delete()
    otp_data.delete();
    if not user_data and otp_data:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    else:
        if password != password2:
            return Response({"Status": "Failed", "Message": "Two Passwords Should be Same"},
                            status=status.HTTP_409_CONFLICT)
        # if user_serializer.is_valid():
        try:
            if len(password) >= 8:
                user_data.set_password(password)
                user_data.save()
                subject = 'Margey Labs - Password Changed'
                messsage = f'Hi {user_data.username},' \
                           f' Your password has been changes today ,If you are not done this' \
                           ' activity , Please login to the portal and change password.'
                email_from = email_Id_developer
                print("email", user_data.email)
                recipient_list = user_data.email
                send_mail(subject, messsage, email_from, [recipient_list], fail_silently=False)
                return Response({"status": "successful", "Message": "OTP Authentication successful your password has been changed"},
                                status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"status": "Failed", "Message": "Password must be minimum of length 8 characters"},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Failed", "Message": "Exception"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def send_otp_key(request):
    email = request.data.get('email')
    print("email", email)
    random_key = random.randint(198134, 999999)
    try:
        if email:
            model = OTPVerify(email=email, otpKey=random_key, isVerified=False)
            model.save()
            subject = 'Margey Labs - OTP to Change Password'
            messsage = f'Hi ,' \
                       f' Your OTP to change password is --[{random_key}] ' \
                       f'Please use the above key to change password.'
            email_from = email_Id_developer
            recipient_list = email
            send_mail(subject, messsage, email_from, [recipient_list], fail_silently=False)
            return Response({"Status": "successful", "Message": "OTP Sent to registered Mail Id","frontcopykey":random_key},
                            status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "Failed", "Message": "OTP Generation UnSuccessful"},
                            status=status.HTTP_400_BAD_REQUEST)
    except not email:
        return Response({"Status":data.errors,"Message":"Failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
@permission_classes((AllowAny,))
def generate_otp_sign_up(request):
    email = request.data.get('email')
    user={}
    try:
        user = User.objects.get(email=email)
        if user:
            return Response(
                {"Status": "Failed", "error": "Above Mail is already registered with us"},
                status=status.HTTP_409_CONFLICT)
    except:
        print("")
    if not user:
        random_key = random.randint(198134, 999999)
        try:
            if email:
                model = OTPVerify(email=email, otpKey=random_key, isVerified=False)
                model.save()
                subject = 'Margey Labs - OTP to Create Account'
                messsage = f'Hi ,' \
                           f' Your OTP to change password is -- {random_key}  -- ' \
                           f'Please use the above key to Create Account.'
                email_from = email_Id_developer
                recipient_list = email
                send_mail(subject, messsage, email_from, [recipient_list], fail_silently=False)
                return Response(
                    {"Status": "successful", "Message": "OTP Sent to registered Mail Id", "frontcopykey": random_key},
                    status=status.HTTP_201_CREATED)
            else:
                return Response({"Status": "Failed", "Message": "OTP Generation UnSuccessful"},
                                status=status.HTTP_400_BAD_REQUEST)
        except not email:
            return Response({"Status": data.errors, "Message": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def add_item(request):
    serializer = ItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response({"Status": "Added"}, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def modify_user(request):
    # user_data = authenticate(username=request.data.get("username"), password=request.data.get("password"))
    user_data = User.objects.get(id=request.data.get('id'))
    if not user_data:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    else:
        user_data.username = request.data.get('username')
        user_data.first_name = request.data.get('first_name')
        user_data.last_name = request.data.get('last_name')
        try:
            user_data.save()
            print("user", user_data)
            return Response({'Status': 'Successful', 'user': UserSerializer(user_data).data},
            status= status.HTTP_202_ACCEPTED)
        except:
            return Response({'Status': 'Failed'},
            status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def change_password(request):
    old_password = request.data.get('old_password')
    password = request.data.get('new_password')
    user_data = User.objects.get(email=request.data.get("email"))
    user = authenticate(username=user_data.username, password=old_password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    else:
        if old_password == password:
            return Response({"Status": "Failed", "Message": "New and old passwords both should be different"},
                            status=status.HTTP_409_CONFLICT)
        # if user_serializer.is_valid():
        try:
            if len(password)>=8:
                user.set_password(password)
                user.save()
                subject = 'Margey Labs - Password Changed'
                messsage = f'Hi {user.username},' \
                           f' Your password has been changes today ,If you are not done this' \
                           ' activity , Please login to the portal and change password.'
                email_from = email_Id_developer
                recipient_list = user.email
                send_mail(subject, messsage, email_from, [recipient_list], fail_silently=False)
                return Response({"status": "successful"}, status=status.HTTP_202_ACCEPTED)
            else:
                return Response({"status": "Failed", "Message": "Password must be minimum of length 8 characters"},
                                status=status.HTTP_400_BAD_REQUEST)
        except:
            return Response({"status": "Failed", "Message": "Exception"}, status=status.HTTP_400_BAD_REQUEST)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def google_login(request):
    token = request.data.get('google_token')
    user={}
    try:
        user = User.objects.get(email=request.data.get('email'))
    except:
        print("User DOes not Exist")
    if not user:
        if token:
            datanew = {
                "username": request.data.get('email').split('@')[0],
                "email": request.data.get('email'),
                "password": 'M@rgey@123',
                "password2": 'M@rgey@123',
                "first_name": request.data.get('first_name'),
                "last_name": request.data.get('last_name')
            }
            serializer = UserSerializer(data=datanew)
            serializer.is_valid(raise_exception=True)
            user = serializer.save()
            user.set_password('M@rgey@123')
            user.save()
            token, _ = Token.objects.get_or_create(user=user)
            subject = 'Margey Labs - Google Authentication Successful'
            messsage = f'Hello {user.username},' \
                       f'Your Authentication using Google Auth with Margey Labs has been Successful , You can login Directly with' \
                       f'Email Id and the default Password [M@rgey@123], You can change password in the portal.'
            email_from = email_Id_developer
            recipient_list = user.email
            send_mail(subject, messsage, email_from, [recipient_list], fail_silently=False)
            return Response({
                "user": UserSerializer(user, context=serializer).data,
                "token": token.key
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({"Status": "Failed", "data": request.data}, status=status.HTTP_400_BAD_REQUEST)
    else:
        token, _ = Token.objects.get_or_create(user=user)
        subject = 'Margey Labs - Google Authentication Successful'
        messsage = f'Hello {user.username},' \
                   f'Your Authentication using Google Auth with Margey Labs has been Successful , You can login Directly with' \
                   f'Email Id and the default Password, You can change password in the portal.'
        email_from = email_Id_developer
        recipient_list = user.email
        send_mail(subject, messsage, email_from, [recipient_list], fail_silently=True)
        return Response({
            "user": UserSerializer(user).data,
            "token": token.key
        }, status=status.HTTP_200_OK)


@csrf_exempt
@api_view(["POST"])
@permission_classes((AllowAny,))
def login(request):
    user = User.objects.get(email=request.data.get("email"))
    username = user.username
    password = request.data.get("password")
    if username is None or password is None:
        return Response({'error': 'Please provide both username and password'},
                        status=HTTP_400_BAD_REQUEST)
    user = authenticate(username=username, password=password)
    if not user:
        return Response({'error': 'Invalid Credentials'}, status=HTTP_404_NOT_FOUND)
    token, _ = Token.objects.get_or_create(user=user)
    return Response({
        "user": UserSerializer(user).data,
        "token": token.key
    }, status=HTTP_200_OK)


@api_view(["GET"])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def Logout(request):
    try:
        request.user.auth_token.delete()
        return Response({"Logged_out": True}, status=status.HTTP_200_OK)
    except:
        return Response({"Logged_out": False}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((AllowAny,))
def create_auth(request):
    serialized = UserSerializer(data=request.DATA)
    if serialized.is_valid():
        User.objects.create_user(
            serialized.init_data['email'],
            serialized.init_data['username'],
            serialized.init_data['password']
        )
        return Response(serialized.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serialized.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_personal_details(request):
    serializer = PersonalDetailsSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = PersonalDetailsSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_hobbie_details(request):
    serializer = InterestsHobbiesSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = InterestsHobbiesSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_language_details(request):
    serializer = LanguagesSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = LanguagesSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_trainings_certificates_details(request):
    serializer = TrainingCertificatesSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = TrainingCertificatesSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_skill(request):
    serializer = SkillSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = SkillSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_education(request):
    serializer = EducationSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = EducationSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_experience(request):
    serializer = ExperienceSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = ExperienceSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_project(request):
    serializer = ProjectSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = ProjectSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_career_objective(request):
    serializer = CareerObjectiveSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = CareerObjectiveSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def register_resume_builder(request):
    serializer = ResumeBuilderSerializer(data=request.data)
    if serializer.is_valid():
        result = serializer.save()
        serializer_data = ResumeBuilderSerializer(result)
        return Response(serializer_data.data, status=status.HTTP_201_CREATED)

    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_personal_details(request):
    id = dict(request.data)['id'][0]
    fullName = dict(request.data)['fullName'][0]
    emailId = dict(request.data)['emailId'][0]
    contactNo = dict(request.data)['contactNo'][0]
    country = dict(request.data)['country'][0]
    state = dict(request.data)['state'][0]
    district = dict(request.data)['district'][0]
    githubProfile = dict(request.data)['githubProfile'][0]
    linkedInProfile = dict(request.data)['linkedInProfile'][0]
    codingProfile = dict(request.data)['codingProfile'][0]
    try:
        PersonalDetails.objects.filter(id=id).update(fullName=fullName,
                                                     contactNo=contactNo,
                                                     country=country,
                                                     state=state,
                                                     district=district,
                                                     githubProfile=githubProfile,
                                                     linkedInProfile=linkedInProfile,
                                                     codingProfile=codingProfile)
        return Response({"Status": "Modified"}, status=status.HTTP_202_ACCEPTED)
    except PersonalDetails.DoesNotExist:
        return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_experience_details(request):
    id = dict(request.data)['id'][0]
    employer = dict(request.data)['employer'][0]
    jobTitle = dict(request.data)['jobTitle'][0]
    country = dict(request.data)['country'][0]
    state = dict(request.data)['state'][0]
    city = dict(request.data)['city'][0]
    jobDescription = dict(request.data)['jobDescription'][0]
    experience = dict(request.data)['experience'][0]
    fromDate = dict(request.data)['fromDate'][0]
    toDate = dict(request.data)['toDate'][0]
    try:
        Experience.objects.filter(id=id).update(employer=employer,
                                                     jobTitle=jobTitle,
                                                     country=country,
                                                     state=state,
                                                     city=city,
                                                     jobDescription=jobDescription,
                                                     experience=experience,
                                                     fromDate=fromDate,
                                                     toDate=toDate)
        return Response({"Status": "Modification Successful"}, status=status.HTTP_202_ACCEPTED)
    except Experience.DoesNotExist:
        return Response({"status": "Failed"}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_personal_details(request):
    id = request.data['id']
    try:
        PersonalDetails.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except PersonalDetails.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_hobbie_details(request):
    id = request.data['id']
    try:
        InterestesHobbies.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except InterestesHobbies.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_language_details(request):
    id = request.data['id']
    try:
        Languages.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except Languages.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_training_certificate_details(request):
    id = request.data['id']
    try:
        TrainingCertificates.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except TrainingCertificates.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_project_details(request):
    id = request.data['id']
    try:
        Project.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except Project.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_experience_details(request):
    id = request.data['id']
    try:
        Experience.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except Experience.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_education_details(request):
    id = request.data['id']
    try:
        Education.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except Education.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_skill_details(request):
    id = request.data['id']
    try:
        Skill.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except Skill.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_career_objective_details(request):
    id = request.data['id']
    try:
        CareerObjective.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except CareerObjective.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def delete_resume_details(request):
    id = request.data['id']
    try:
        ResumeBuilder.objects.get(id=id).delete()
        return Response({"Status": "Deleted"}, status=status.HTTP_200_OK)
    except ResumeBuilder.DoesNotExist:
        return Response({"Status": "Failed"}, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_personal_details(request):
    details = PersonalDetails.objects.all()
    serializer = PersonalDetailsSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_projects(request):
    details = Project.objects.all()
    serializer = ProjectSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_skills(request):
    details = Skill.objects.all()
    serializer = SkillSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_experiences(request):
    details = Experience.objects.all()
    serializer = ExperienceSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_education_list(request):
    details = Education.objects.all()
    serializer = EducationSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_resumes(request):
    details = ResumeBuilder.objects.all()
    serializer = ResumeBuilderSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_all_career_objectives(request):
    details = CareerObjective.objects.all()
    serializer = CareerObjectiveSerializer(details, many=True)
    return Response({"Details": serializer.data}, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_experience_data(request, pk):
    try:
        experience = Experience.objects.get(pk=pk)
    except Experience.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ExperienceSerializer(experience)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_hobbie_data(request, pk):
    try:
        hobbie = InterestesHobbies.objects.get(pk=pk)
    except InterestesHobbies.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = InterestsHobbiesSerializer(hobbie)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_language_data(request, pk):
    try:
        language = Languages.objects.get(pk=pk)
    except InterestesHobbies.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = LanguagesSerializer(language)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_training_certificates_data(request, pk):
    try:
        certificate = TrainingCertificates.objects.get(pk=pk)
    except TrainingCertificates.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = TrainingCertificatesSerializer(certificate)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_personal_data(request, pk):
    try:
        personal = PersonalDetails.objects.get(pk=pk)
    except PersonalDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = PersonalDetailsSerializer(personal)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_skills_data(request, pk):
    try:
        skill = Skill.objects.get(pk=pk)
    except Skill.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = SkillSerializer(skill)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_education_data(request, pk):
    try:
        education = Education.objects.get(pk=pk)
    except Education.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = EducationSerializer(education)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_career_objective_data(request, pk):
    try:
        career_objective = CareerObjective.objects.get(pk=pk)
    except CareerObjective.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CareerObjectiveSerializer(career_objective)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_resume_data(request, pk):
    try:
        resume = ResumeBuilder.objects.get(pk=pk)
    except ResumeBuilder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ResumeBuilderSerializer(resume)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_personal_data_by_id(request):
    print('data', request.data)
    try:
        resume = PersonalDetails.objects.get(emailId=request.data.get('emailId'))
    except PersonalDetails.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    if request.method == 'POST':
        serializer = PersonalDetailsSerializer(resume)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_resume_data_by_id(request):
    print('data', request.data)
    try:
        resume = ResumeBuilder.objects.get(emailId=request.data.get('emailId'))
        print('data', request.data)
    except ResumeBuilder.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'POST':
        serializer = ResumeBuilderSerializer(resume)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def get_project_data(request, pk):
    try:
        project = Project.objects.get(pk=pk)
    except Project.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProjectSerializer(project)
        return Response(serializer.data, status=status.HTTP_200_OK)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_resume_data(request, pk):
    resume = ResumeBuilder.objects.get(pk=pk)
    resume_data = JSONParser().parse(request)
    print("resume_data", resume_data)
    resume_serializer = ResumeBuilderSerializer(resume, data=resume_data)
    if resume_serializer.is_valid():
        try:
            resume_serializer.save()
            return JsonResponse(resume_serializer.data, status=status.HTTP_202_ACCEPTED)
        except resume_serializer.errors:
            return JsonResponse(resume_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_skills_data(request, pk):
    skill = Skill.objects.get(pk=pk)
    skill_data = JSONParser().parse(request)
    skill_serializer = SkillSerializer(skill, data=skill_data)
    if skill_serializer.is_valid():
        try:
            skill_serializer.save()
            return JsonResponse(skill_serializer.data, status=status.HTTP_202_ACCEPTED)
        except skill_serializer.errors:
            return JsonResponse(skill_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_education_data(request, pk):
    education = Education.objects.get(pk=pk)
    education_data = JSONParser().parse(request)
    education_serializer = EducationSerializer(education, data=education_data)
    if education_serializer.is_valid():
        try:
            education_serializer.save()
            return JsonResponse(education_serializer.data, status=status.HTTP_202_ACCEPTED)
        except education_serializer.errors:
            return JsonResponse(education_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_experience_data(request, pk):
    experience = Experience.objects.get(pk=pk)
    experience_data = JSONParser().parse(request)
    experience_serializer = ExperienceSerializer(experience, data=experience_data)
    if experience_serializer.is_valid():
        try:
            experience_serializer.save()
            return JsonResponse(experience_serializer.data, status=status.HTTP_202_ACCEPTED)
        except experience_serializer.errors:
            return JsonResponse(experience_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_personal_data(request, pk):
    personal = PersonalDetails.objects.get(pk=pk)
    personal_data = JSONParser().parse(request)
    personal_serializer = PersonalDetailsSerializer(personal, data=personal_data)
    if personal_serializer.is_valid():
        try:
            personal_serializer.save()
            return JsonResponse(personal_serializer.data, status=status.HTTP_202_ACCEPTED)
        except personal_serializer.errors:
            return JsonResponse(personal_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_career_objective_data(request, pk):
    career = CareerObjective.objects.get(pk=pk)
    career_data = JSONParser().parse(request)
    career_serializer = CareerObjectiveSerializer(career, data=career_data)
    if career_serializer.is_valid():
        try:
            career_serializer.save()
            return JsonResponse(career_serializer.data, status=status.HTTP_202_ACCEPTED)
        except career_serializer.errors:
            return JsonResponse(career_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_project_data(request, pk):
    project = Project.objects.get(pk=pk)
    project_data = JSONParser().parse(request)
    project_serializer = ProjectSerializer(project, data=project_data)
    if project_serializer.is_valid():
        try:
            project_serializer.save()
            return JsonResponse(project_serializer.data, status=status.HTTP_202_ACCEPTED)
        except project_serializer.errors:
            return Response(project_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_language_data(request, pk):
    language = Languages.objects.get(pk=pk)
    language_data = JSONParser().parse(request)
    language_serializer = LanguagesSerializer(language, data=language_data)
    if language_serializer.is_valid():
        try:
            language_serializer.save()
            return JsonResponse(language_serializer.data, status=status.HTTP_202_ACCEPTED)
        except language_serializer.errors:
            return Response(language_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_hobbie_data(request, pk):
    hobbie = InterestesHobbies.objects.get(pk=pk)
    hobbie_data = JSONParser().parse(request)
    hobbie_serializer = LanguagesSerializer(hobbie, data=hobbie_data)
    if hobbie_serializer.is_valid():
        try:
            hobbie_serializer.save()
            return JsonResponse(hobbie_serializer.data, status=status.HTTP_202_ACCEPTED)
        except hobbie_serializer.errors:
            return Response(hobbie_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@authentication_classes([TokenAuthentication])
@authentication_classes([IsAuthenticated])
def modify_training_certificates_data(request, pk):
    certificate = TrainingCertificates.objects.get(pk=pk)
    certificate_data = JSONParser().parse(request)
    certificate_serializer = LanguagesSerializer(certificate, data=certificate_data)
    if certificate_serializer.is_valid():
        try:
            certificate_serializer.save()
            return JsonResponse(certificate_serializer.data, status=status.HTTP_202_ACCEPTED)
        except certificate_serializer.errors:
            return Response(certificate_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


def send_mail_to_user(self,subject, message, email_from, recipient_list):
    send_mail('Hello', 'Hello there please be cool', 'sagarreddyguvvala.77@gmail.com', ['sampusharma040@gmail.com'],
              fail_silently= False)
    send_mail(subject, message, email_from, recipient_list)

