from django.db import models
from django.utils.translation import ugettext as _


class Document(models.Model):
    name = models.CharField(max_length=255)
    document = models.FileField(upload_to='documents')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Document")
        verbose_name_plural = _("Documents")

    def __str__(self):
        return self.name

class DocumentDetail(models.Model):
    document = models.ForeignKey(Document, related_name='document_name', on_delete=models.CASCADE)
    patient_name = models.CharField(verbose_name="Patient's Name", max_length=200, null=True, blank=True)
    dob = models.CharField(verbose_name="DOB", max_length=200, null=True, blank=True)
    sex = models.CharField(verbose_name="Sex", max_length=200, null=True, blank=True)
    date_of_surgery = models.CharField(verbose_name="Date of Surgery", max_length=200, null=True, blank=True)
    claim_no = models.CharField(verbose_name="Claim No", max_length=200, null=True, blank=True)
    address = models.TextField(verbose_name="Address", null=True, blank=True)
    injury = models.TextField(verbose_name="Injury", null=True, blank=True)
    allergies = models.TextField(verbose_name="Allergies", null=True, blank=True)
    social_history = models.TextField(verbose_name="Social History", null=True, blank=True)
    medical_history = models.TextField(verbose_name="Medical History", null=True, blank=True)
    impression = models.TextField(verbose_name="Impression", null=True, blank=True)
    medicines = models.TextField(verbose_name="medicines", null=True, blank=True)
    vital_signs = models.TextField(verbose_name="vital_signs", null=True, blank=True)
    doctor = models.CharField(verbose_name="Doctor's Name", max_length=200, null=True, blank=True)
    general = models.TextField(verbose_name="general", null=True, blank=True)

    class Meta:
        verbose_name = _("Document Detail")
        verbose_name_plural = _("Document Details")

    def __str__(self):
        return self.document.name


