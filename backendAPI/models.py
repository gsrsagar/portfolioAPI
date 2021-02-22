from django.db import models
# Create your models here.


class Item(models.Model):
    Item_Id = models.IntegerField()
    ItemName = models.CharField(max_length=300)
    Price = models.FloatField()
    Quantity = models.IntegerField()
    Category = models.CharField(max_length=200)

    def __str__(self):
        return self.ItemName


class Education(models.Model):
    id = models.AutoField(primary_key=True)
    educationType = models.CharField(max_length=300)
    institutionName = models.CharField(max_length=300)
    branch = models.CharField(max_length=100, null=True, blank=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    yearOfPassing = models.IntegerField()
    percentage = models.IntegerField()
    startDate = models.DateField()
    endDate = models.DateField()

    def __str__(self):
        return self.educationType


class PersonalDetails(models.Model):
    id = models.AutoField(primary_key=True)
    fullName = models.CharField(max_length=100)
    emailId = models.EmailField(unique=True)
    contactNo = models.CharField(max_length=100, unique=True)
    district = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    githubProfile = models.CharField(max_length=200, null=True, blank=True)
    linkedInProfile = models.CharField(max_length=200, null=True, blank=True)
    codingProfile = models.CharField(max_length=300, null=True, blank=True)

    def __str__(self):
        return self.emailId


class Skill(models.Model):
    id = models.AutoField(primary_key=True)
    skill = models.CharField(max_length=200)
    skillClass = models.CharField(max_length=200)
    skillClassIndex = models.IntegerField()

    def __str__(self):
        return self.skill


class Experience(models.Model):
    id = models.AutoField(primary_key=True)
    employer = models.CharField(max_length=100)
    jobTitle = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    jobDescription = models.TextField()
    experience = models.FloatField()
    fromDate = models.DateField()
    toDate = models.DateField(null=True, blank=True)
    present = models.BooleanField(null=True, blank=True)

    def __str__(self):
        return self.employer


class CareerObjective(models.Model):
    id = models.AutoField(primary_key=True)
    careerObjective = models.TextField(max_length=2000, unique=False)

    def __str__(self):
        return self.careerObjective


class TrainingCertificates(models.Model):
    id = models.AutoField(primary_key=True)
    trainAndCertificates = models.TextField(max_length=2000, unique=False)

    def __str__(self):
        return self.trainAndCertificates


class Languages(models.Model):
    id = models.AutoField(primary_key=True)
    language = models.TextField(max_length=200, unique=False)

    def __str__(self):
        return self.language


class InterestesHobbies(models.Model):
    id = models.AutoField(primary_key=True)
    hobby = models.TextField(max_length=200, unique=False)

    def __str__(self):
        return self.hobby


class Project(models.Model):
    id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=200)
    description = models.TextField()
    skills = models.ManyToManyField(Skill)
    link = models.CharField(max_length=200, null=True, blank=True)

    def __str__(self):
        return self.title


class ResumeBuilder(models.Model):
    id = models.AutoField(primary_key=True)
    personalDetails = models.OneToOneField(PersonalDetails, on_delete=models.CASCADE, null=True, blank=True, unique=False)
    education = models.ManyToManyField(Education, null=True, blank=True, unique=False)
    skills = models.ManyToManyField(Skill, null=True, blank=True, unique=False)
    experience = models.ManyToManyField(Experience, null=True, blank=True, unique=False)
    project = models.ManyToManyField(Project, null=True, blank=True, unique=False)
    careerObjective = models.OneToOneField(CareerObjective, null=True, blank=True, on_delete=models.CASCADE, unique=False)
    trainingCertificates = models.ManyToManyField(TrainingCertificates,  null=True, blank=True, unique=False)
    languages = models.ManyToManyField(Languages, null=True, blank=True, unique=False)
    interestesHobbies = models.ManyToManyField(InterestesHobbies, null=True, blank=True, unique=False)
    emailId = models.EmailField(unique=True)

    def __str__(self):
        return self.personalDetails.emailId


class OTPVerify(models.Model):
    id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=False)
    otpKey = models.IntegerField()
    isVerified = models.BooleanField()

    def __str__(self):
        return self.email
