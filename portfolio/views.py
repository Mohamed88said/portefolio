from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import TemplateView, ListView, DetailView, FormView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.utils.translation import gettext_lazy as _
from .models import (
    Profile, Education, Experience, Skill, 
    Certification, Project, Contact, SiteSettings
)
from .forms import ContactForm
import json

class BaseView(TemplateView):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        try:
            context['profile'] = Profile.objects.first()
            context['site_settings'] = SiteSettings.objects.first()
        except:
            context['profile'] = None
            context['site_settings'] = None
        return context

class HomeView(BaseView):
    template_name = 'portfolio/home.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_projects'] = Project.objects.filter(is_featured=True)[:3]
        context['featured_skills'] = Skill.objects.filter(is_featured=True)
        context['recent_experiences'] = Experience.objects.all()[:3]
        return context

class AcademicView(BaseView):
    template_name = 'portfolio/academic.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['educations'] = Education.objects.all()
        context['skills'] = Skill.objects.all()
        return context

class ExperienceView(BaseView):
    template_name = 'portfolio/experience.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['experiences'] = Experience.objects.all()
        return context

class CertificationView(BaseView):
    template_name = 'portfolio/certifications.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['certifications'] = Certification.objects.all()
        return context

class ProjectListView(BaseView, ListView):
    model = Project
    template_name = 'portfolio/projects.html'
    context_object_name = 'projects'
    paginate_by = 6

class ProjectDetailView(BaseView, DetailView):
    model = Project
    template_name = 'portfolio/project_detail.html'
    context_object_name = 'project'

class ContactView(BaseView, FormView):
    template_name = 'portfolio/contact.html'
    form_class = ContactForm
    success_url = '/contact/success/'
    
    def form_valid(self, form):
        # Sauvegarder le message
        contact = form.save()
        
        # Envoyer l'email
        try:
            send_mail(
                subject=f"Nouveau message de {contact.name}: {contact.subject}",
                message=f"De: {contact.name} ({contact.email})\n\nMessage:\n{contact.message}",
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[settings.EMAIL_HOST_USER],
                fail_silently=False,
            )
        except Exception as e:
            messages.error(self.request, _("Erreur lors de l'envoi de l'email."))
        
        messages.success(self.request, _("Votre message a été envoyé avec succès!"))
        return super().form_valid(form)

class ContactSuccessView(BaseView):
    template_name = 'portfolio/contact_success.html'

@method_decorator(csrf_exempt, name='dispatch')
class ContactAPIView(TemplateView):
    def post(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body)
            contact = Contact.objects.create(
                name=data.get('name'),
                email=data.get('email'),
                subject=data.get('subject'),
                message=data.get('message')
            )
            
            # Envoyer l'email
            try:
                send_mail(
                    subject=f"Nouveau message de {contact.name}: {contact.subject}",
                    message=f"De: {contact.name} ({contact.email})\n\nMessage:\n{contact.message}",
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[settings.EMAIL_HOST_USER],
                    fail_silently=False,
                )
            except:
                pass
            
            return JsonResponse({'success': True, 'message': 'Message envoyé avec succès!'})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})