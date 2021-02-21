from rest_framework.validators import UniqueValidator
from django.contrib.auth.password_validation import validate_password
from .models import Item, Education, Skill, Experience, CareerObjective, PersonalDetails, ResumeBuilder, Project, OTPVerify, InterestesHobbies, Languages, TrainingCertificates
from django.contrib.auth.models import User, Group
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class OTPVerifySerializer(serializers.ModelSerializer):
    class Meta:
        model = OTPVerify
        fields = ('id', 'email', 'otpKey', 'isVerified')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ['url', 'name']


class EducationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Education
        fields = '__all__'


class SkillSerializer(serializers.ModelSerializer):
    class Meta:
        model = Skill
        fields = '__all__'


class ExperienceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Experience
        fields = '__all__'


class CareerObjectiveSerializer(serializers.ModelSerializer):
    class Meta:
        model = CareerObjective
        fields = '__all__'


class InterestsHobbiesSerializer(serializers.ModelSerializer):
    class Meta:
        model = InterestesHobbies
        fields = '__all__'


class LanguagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = Languages
        fields = '__all__'       


class TrainingCertificatesSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingCertificates
        fields = '__all__'


class PersonalDetailsSerializer(serializers.ModelSerializer):
    class Meta:
        model = PersonalDetails
        fields = '__all__'


class ResumeBuilderSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResumeBuilder
        fields = '__all__'


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = '__all__'


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )

    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'password2', 'email', 'first_name', 'last_name')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            username=validated_data['username'],
            email=validated_data['email'],
            first_name=validated_data['first_name'],
            last_name=validated_data['last_name']
        )

        user.set_password(validated_data['password'])
        user.save()

        return user

