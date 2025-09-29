from django import forms
from .models import Company, Contact, EmailLog

class CompanyForm(forms.ModelForm):
    class Meta:
        model = Company
        fields = ['name', 'address', 'phone', 'website', 'description']

class ContactForm(forms.ModelForm):
    class Meta:
        model = Contact
        fields = "__all__"

class EmailForm(forms.Form):
    recipient = forms.EmailField(label='Empfänger')
    subject = forms.CharField(label='Betreff', max_length=255)
    body = forms.CharField(label='Nachricht', widget=forms.Textarea)


# crm_core/forms.py
from django import forms
from .models import FileAsset

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = FileAsset
        fields = ["file", "company", "contact", "notes"]

    def save(self, commit=True):
        obj = super().save(commit=False)
        f = self.cleaned_data.get("file")
        if f:
            obj.original_name = f.name
            obj.size = f.size
        if commit:
            obj.save()
        return obj
