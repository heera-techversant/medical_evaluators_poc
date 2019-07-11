import re
from django.shortcuts import render
from django.views import generic
from django.template import RequestContext
from evaluators.models import Document, DocumentDetail
from evaluators.forms import DocumentForm
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from django.contrib.auth import authenticate, login, logout
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO
from PIL import Image
from pytesseract import image_to_string
from django.shortcuts import redirect, render, render_to_response, HttpResponseRedirect
from evaluators.forms import SignUpForm, LoginForm

class LoginView(generic.TemplateView):
    template_name = 'login.html'

    def post(self, request, *args, **kwargs):
        form = LoginForm(request.POST)
        kwargs['form'] = form
        print(form.errors, 'errordsss')
        if form.is_valid():
            email = request.POST['email']
            password = request.POST['password']
            user = authenticate(username=email, password=password)
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return redirect('home')
        return render(request, self.template_name, self.get_context_data(**kwargs), RequestContext(request))

    # def dispatch(self, request, *args, **kwargs):
    #     """
    #     if the user is logged in, redirect from login page to profile page
    #
    #
    #     """
    #     if self.request.user.is_authenticated():
    #         return redirect('signin')
    #     return super(LoginView, self).dispatch(request, *args, **kwargs)

def logout_view(request):
    logout(request)
    return redirect('signin')

class SignUpView(generic.FormView):
    template_name = 'register.html'
    form_class = SignUpForm
    success_url = 'signin'

    def post(self, request, *args, **kwargs):
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            username = form.cleaned_data.get('username')
            user.email = username
            user.save()
            return redirect('signin')
        else:
            form = SignUpForm()
        return render(request, 'register.html', {'form': form})

class HomeView(generic.CreateView):
    template_name = 'index.html'
    form_class = DocumentForm
    success_url = '/doc_save'

class DocumentListView(generic.TemplateView):
    template_name = 'document_list.html'

    def get_context_data(self, **kwargs):
        context = {}
        document_list = Document.objects.all().order_by('-uploaded_at')
        context['documents'] = document_list
        return context

class DocumentDetailView(generic.TemplateView):
    template_name = 'document_detail.html'

    def get_context_data(self, **kwargs):
        doc_id = kwargs['doc_id']
        document_obj = DocumentDetail.objects.get(document__id=doc_id)
        return {'doc_obj':document_obj}


class DocsaveView(generic.TemplateView):
    template_name = 'view_profile.html'

    def get_context_data(self, **kwargs):
        context = {}
        document_obj = Document.objects.filter().order_by('-uploaded_at')[0]
        context['document_name'] = document_obj.name
        path = document_obj.document.path
        context['path'] = path
        doc_detail = DocumentDetail(document=document_obj)

        if path.endswith('.pdf'):
            rsrcmgr = PDFResourceManager()
            retstr = StringIO()
            codec = 'utf-8'
            laparams = LAParams()
            device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
            fp = open(path, 'rb')
            interpreter = PDFPageInterpreter(rsrcmgr, device)
            password = ""
            maxpages = 0
            caching = True
            pagenos = set()
            for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password, caching=caching,
                                          check_extractable=True):
                interpreter.process_page(page)
            text = retstr.getvalue()
            fp.close()
            device.close()
            retstr.close()
            #
            # with open("testtttttttttt.txt", "w") as text_file:
            #     text_file.write(text)

            text = text.lower()
            name = re.findall(r"patient's name:|patient:(.*)", text.lower())
            if not name:
                name = re.findall(r"re:(.*)", text.lower())
            address = self.__remove_null_from_list(re.findall(r"address:(.*)", text.lower()))
            dob = self.__remove_null_from_list(re.findall(r"dob:(.*),", text.lower()))
            if not dob:
                dob = re.findall(r"date of birth:\s*(.*)", text.lower())
            sex = re.findall(r"sex:(.*)", text.lower())
            injury = re.findall(r"consultation:(.+?)\.", text, re.DOTALL)
            if not injury:
                injury = self.__remove_null_from_list(re.findall(r"injury:(.*)", text.lower()))
            date_of_surgery = re.findall(r"date of surgery:(.*)", text.lower())
            claim_no = re.findall(r"(claim #|claim#:)(.*)", text.lower())
            allergies = self.__remove_null_from_list(re.findall(r"allergies:(.*)", text.lower()))
            social_history = re.findall(r"(social history|family history|social  history :)(.*?)(?:(?:\r*\n){2})", text.lower(), re.DOTALL)
            if 'no past medical history on file' in text.lower():
                medical_history = ['no past medical history on file']
            else:
                medical_history = re.findall(r"medical history:(.+?)\.", text.lower(), re.DOTALL)
            impression_list = re.findall(r"(impression.*?)(?:(?:\r*\n){2})", text.lower(), re.DOTALL)
            impression = [i.replace('impression: ','') for i in impression_list]
            impression = list(filter(None, impression))
            doctor = re.findall(r"(doctor.|physician:)(.*)", text.lower())
            medicines = re.findall(r'mar action  action date  dose(.+?)iven', text.lower(), re.DOTALL)
            if medicines:
                medicine_list = list(filter(None, medicines[0].split('\n')))
                medicines_list = ''.join(medicine_list[3:])
            if not medicines:
                medicines = re.findall(r'current  medications :(.+?)groves, steven j', text.lower(), re.DOTALL)
                medicines_list = list(filter(None, medicines[0].split('\n')))
                del medicines_list[5:11]
                medicines_list = ''.join(medicines_list[1:])

            general = re.findall(r'general:(.*)', text.lower())[1]
            vital_signs = re.findall(r'last filed vital signs(.+?)vital\s*s~ig', text, re.DOTALL)
            if not vital_signs:
                vital_dict = {}
                vital_sign_string = ''
                vital_signss = re.findall(r'vital signs:(.+?)bilateral', text.lower(), re.DOTALL)
                vital_signss = list(filter(None, vital_signss[0].split('\n')))
                vital_dict['blood_pressure'] = vital_signss[-8].strip()
                vital_dict['pulse'] = vital_signss[-7].strip()
                vital_dict['temperature'] = vital_signss[-6].strip()
                vital_dict['respiratory_rate'] = vital_signss[-5].strip()
                vital_dict['Body Mass Index'] = vital_signss[-1].strip()
                vital_dict['Sp02'] = vital_signss[-2].strip()
                vital_dict['Weight'] = vital_signss[-3].strip()
                vital_dict['Height'] = vital_signss[-4].strip()
                for key, value in vital_dict.items():
                    vital_sign_string += key
                    vital_sign_string += " : " + value + ', '

            if vital_signs:
                vital_sign_string = ''
                vital_dict = {}
                vital_signs = vital_signs[0].split('\n')
                vital_dict['blood_pressure'] = vital_signs[4].strip().strip('·').strip()
                vital_dict['pulse'] = vital_signs[5].strip()
                vital_dict['temperature'] = vital_signs[6].strip()
                vital_dict['respiratory_rate'] = vital_signs[7].strip()
                vital_dict['oxygen_sat'] = vital_signs[8].strip()
                for key, value in vital_dict.items():
                    vital_sign_string += key
                    vital_sign_string += " : " + value + ', '
            context['name'] = ''
            context['address'] = ''
            context['dob'] = ''
            context['sex'] = ''
            context['date_of_surgery'] = ''
            context['doctor'] = ''
            if name:
                context['name'] = name[-1].replace('(cid:9)','').strip()
                doc_detail.patient_name = context['name']
            if address:
                context['address'] = address[-1].replace('(cid:9)','').strip()
                doc_detail.address = context['address']
            if dob:
                context['dob'] = dob[-1].replace('(cid:9)','').strip()
                doc_detail.dob = context['dob']
            if sex:
                context['sex'] = sex[-1].replace('(cid:9)','').strip()
                doc_detail.sex = context['sex']
            if date_of_surgery:
                context['date_of_surgery'] = date_of_surgery[-1].replace('(cid:9)','').strip()
                doc_detail.date_of_surgery = context['date_of_surgery']
            if injury:
                context['injury'] = injury[0]
                doc_detail.injury = context['injury']
            if claim_no:
                context['claim_no'] = claim_no[0][1]
                doc_detail.claim_no = context['claim_no']
            if allergies:
                context['allergies'] = allergies[0]
                doc_detail.allergies = context['allergies']
            if social_history:
                context['social_history'] = social_history[0][1]
                doc_detail.social_history = context['social_history']
            if medical_history:
                context['medical_history'] = medical_history[0]
                doc_detail.medical_history = context['medical_history']
            if impression:
                context['impression'] = impression[0]
                doc_detail.impression = context['impression']
            if doctor:
                context['doctor'] = doctor[0][1]
                doc_detail.doctor = context['doctor']
            if vital_sign_string:
                context['vital_signs'] = vital_sign_string.strip().strip(',')
                doc_detail.vital_signs = context['vital_signs']
            if medicines_list:
                context['medicines'] = medicines_list
                doc_detail.medicines = context['medicines']
            if general:
                context['general'] = general
                doc_detail.general = context['general']
            doc_detail.save()
        return context

    def __remove_null_from_list(self, mylist):
        mylist = [i for i in mylist if i != ' ']
        return mylist