from django import forms
from django.contrib.auth.models import User
from .models import (
    VolunteerProfile, Campaign, Activity, VolunteerAvailability,
    Role, Shift, ShiftAssignment, ParticipationRecord, Announcement
)


class VolunteerRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'gov-input', 'placeholder': 'Enter First Name'
    }))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={
        'class': 'gov-input', 'placeholder': 'Enter Last Name'
    }))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={
        'class': 'gov-input', 'placeholder': 'citizen.volunteer@email.com'
    }))
    username = forms.CharField(max_length=150, required=True, widget=forms.TextInput(attrs={
        'class': 'gov-input', 'placeholder': 'Choose unique username or Mobile No.'
    }))
    password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'gov-input', 'placeholder': 'Enter secure password'
    }))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={
        'class': 'gov-input', 'placeholder': 'Confirm password'
    }))

    class Meta:
        model = VolunteerProfile
        fields = [
            'phone', 'alternate_phone', 'gender', 'blood_group',
            'id_proof_type', 'id_proof_number', 'state', 'district', 'pincode',
            'address', 'occupation', 'skills', 'preferred_sector', 'bio', 'profile_picture'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': '10-digit mobile number'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Optional alternate number'}),
            'gender': forms.Select(attrs={'class': 'gov-select'}),
            'blood_group': forms.Select(attrs={'class': 'gov-select'}),
            'id_proof_type': forms.Select(attrs={'class': 'gov-select'}),
            'id_proof_number': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Enter ID / Aadhaar number'}),
            'state': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'State / UT (e.g. Maharashtra, Delhi, Odisha)'}),
            'district': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'District'}),
            'pincode': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': '6-digit PIN code'}),
            'address': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 2, 'placeholder': 'Permanent / Local Address'}),
            'occupation': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'e.g. College Student, Teacher, IT Engineer, Nurse'}),
            'skills': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'e.g. First Aid, Crowd Control, Teaching, Logistics, Driving'}),
            'preferred_sector': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'e.g. Healthcare, Literacy, Disaster Relief, Food Security'}),
            'bio': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 3, 'placeholder': 'Briefly describe your motivation to serve with the NGO'}),
            'profile_picture': forms.FileInput(attrs={'class': 'gov-file-input'}),
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already taken. Please choose another.")
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("An account with this email address already exists.")
        return email

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        confirm_password = cleaned_data.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match.")
        return cleaned_data


class VolunteerProfileUpdateForm(forms.ModelForm):
    first_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'gov-input'}))
    last_name = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'class': 'gov-input'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'gov-input'}))

    class Meta:
        model = VolunteerProfile
        fields = [
            'phone', 'alternate_phone', 'emergency_contact_name', 'emergency_contact_phone',
            'gender', 'blood_group', 'availability_status', 'state', 'district', 'pincode',
            'address', 'occupation', 'skills', 'preferred_sector', 'bio', 'profile_picture'
        ]
        widgets = {
            'phone': forms.TextInput(attrs={'class': 'gov-input'}),
            'alternate_phone': forms.TextInput(attrs={'class': 'gov-input'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': 'gov-input'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': 'gov-input'}),
            'gender': forms.Select(attrs={'class': 'gov-select'}),
            'blood_group': forms.Select(attrs={'class': 'gov-select'}),
            'availability_status': forms.Select(attrs={'class': 'gov-select'}),
            'state': forms.TextInput(attrs={'class': 'gov-input'}),
            'district': forms.TextInput(attrs={'class': 'gov-input'}),
            'pincode': forms.TextInput(attrs={'class': 'gov-input'}),
            'address': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 2}),
            'occupation': forms.TextInput(attrs={'class': 'gov-input'}),
            'skills': forms.TextInput(attrs={'class': 'gov-input'}),
            'preferred_sector': forms.TextInput(attrs={'class': 'gov-input'}),
            'bio': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'gov-file-input'}),
        }


class AvailabilityForm(forms.ModelForm):
    class Meta:
        model = VolunteerAvailability
        fields = ['day_of_week', 'time_slot', 'notes']
        widgets = {
            'day_of_week': forms.Select(attrs={'class': 'gov-select'}),
            'time_slot': forms.Select(attrs={'class': 'gov-select'}),
            'notes': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Optional area constraint or notes'}),
        }


class CampaignForm(forms.ModelForm):
    class Meta:
        model = Campaign
        fields = [
            'title', 'slug', 'sector', 'short_description', 'detailed_description',
            'banner_image', 'target_beneficiaries', 'target_volunteers',
            'state', 'district', 'venue_address', 'start_date', 'end_date',
            'status', 'emergency_helpline'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Campaign / Mission Title'}),
            'slug': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'unique-campaign-slug'}),
            'sector': forms.Select(attrs={'class': 'gov-select'}),
            'short_description': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Short summary for public notice'}),
            'detailed_description': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 4, 'placeholder': 'Comprehensive mission objectives & operational guidelines'}),
            'banner_image': forms.FileInput(attrs={'class': 'gov-file-input'}),
            'target_beneficiaries': forms.NumberInput(attrs={'class': 'gov-input'}),
            'target_volunteers': forms.NumberInput(attrs={'class': 'gov-input'}),
            'state': forms.TextInput(attrs={'class': 'gov-input'}),
            'district': forms.TextInput(attrs={'class': 'gov-input'}),
            'venue_address': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 2, 'placeholder': 'Base camp / Reporting grounds address'}),
            'start_date': forms.DateInput(attrs={'class': 'gov-input', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'gov-input', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'gov-select'}),
            'emergency_helpline': forms.TextInput(attrs={'class': 'gov-input'}),
        }


class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = [
            'campaign', 'activity', 'title', 'date', 'start_time', 'end_time',
            'reporting_location', 'in_charge_name', 'in_charge_contact',
            'required_volunteers', 'status', 'special_instructions'
        ]
        widgets = {
            'campaign': forms.Select(attrs={'class': 'gov-select'}),
            'activity': forms.Select(attrs={'class': 'gov-select'}),
            'title': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'e.g. Morning Distribution & Triage Duty'}),
            'date': forms.DateInput(attrs={'class': 'gov-input', 'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'class': 'gov-input', 'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'class': 'gov-input', 'type': 'time'}),
            'reporting_location': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Gate number, Room or Landmark'}),
            'in_charge_name': forms.TextInput(attrs={'class': 'gov-input'}),
            'in_charge_contact': forms.TextInput(attrs={'class': 'gov-input'}),
            'required_volunteers': forms.NumberInput(attrs={'class': 'gov-input'}),
            'status': forms.Select(attrs={'class': 'gov-select'}),
            'special_instructions': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 2, 'placeholder': 'Dress code, equipment provided, ID check notice'}),
        }


class RoleAssignmentForm(forms.ModelForm):
    class Meta:
        model = ShiftAssignment
        fields = ['role', 'status', 'admin_notes']
        widgets = {
            'role': forms.Select(attrs={'class': 'gov-select'}),
            'status': forms.Select(attrs={'class': 'gov-select'}),
            'admin_notes': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Instructions for volunteer'}),
        }


class AttendanceMarkForm(forms.ModelForm):
    class Meta:
        model = ParticipationRecord
        fields = ['attendance_status', 'hours_logged', 'performance_rating', 'coordinator_remarks']
        widgets = {
            'attendance_status': forms.Select(attrs={'class': 'gov-select text-sm py-1'}),
            'hours_logged': forms.NumberInput(attrs={'class': 'gov-input text-sm py-1 w-20', 'step': '0.5'}),
            'performance_rating': forms.Select(attrs={'class': 'gov-select text-sm py-1'}),
            'coordinator_remarks': forms.TextInput(attrs={'class': 'gov-input text-sm py-1', 'placeholder': 'Remarks / Merits'}),
        }


class VolunteerFeedbackForm(forms.ModelForm):
    class Meta:
        model = ParticipationRecord
        fields = ['volunteer_feedback']
        widgets = {
            'volunteer_feedback': forms.Textarea(attrs={
                'class': 'gov-textarea', 'rows': 3,
                'placeholder': 'Share your ground observations, challenges faced, or suggestions for future drives.'
            }),
        }


class AnnouncementForm(forms.ModelForm):
    class Meta:
        model = Announcement
        fields = ['title', 'campaign', 'priority', 'message', 'is_published']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'gov-input', 'placeholder': 'Circular or Urgent Notice Title'}),
            'campaign': forms.Select(attrs={'class': 'gov-select'}),
            'priority': forms.Select(attrs={'class': 'gov-select'}),
            'message': forms.Textarea(attrs={'class': 'gov-textarea', 'rows': 3, 'placeholder': 'Official communication message'}),
            'is_published': forms.CheckboxInput(attrs={'class': 'gov-checkbox'}),
        }
