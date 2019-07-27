from django import forms
from object.models import GroupPhoto, SoloPhoto



# ---------------------------------------------------------------------------------

class BAdminGroupPhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    rotate = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = GroupPhoto
        fields = ('file_300', 'file_50', 'x', 'y', 'width', 'height', 'rotate',)


class BAdminSoloPhotoForm(forms.ModelForm):
    x = forms.FloatField(widget=forms.HiddenInput())
    y = forms.FloatField(widget=forms.HiddenInput())
    width = forms.FloatField(widget=forms.HiddenInput())
    height = forms.FloatField(widget=forms.HiddenInput())
    rotate = forms.FloatField(widget=forms.HiddenInput())

    class Meta:
        model = SoloPhoto
        fields = ('file_300', 'file_50', 'x', 'y', 'width', 'height', 'rotate',)