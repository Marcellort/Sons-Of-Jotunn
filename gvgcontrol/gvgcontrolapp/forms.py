from django import forms
from .models import Member

from django.utils.translation import gettext_lazy as _

class MemberForm(forms.ModelForm):
    STATUS_CHOICES = [
        ('active', _('Ativo')),
        ('inactive', _('Inativo')),
    ]
    PAYMENT_CHOICES = [
        ('weekly', _('Semanal')),
        ('monthly', _('Mensal')),
    ]

    class Meta:
        model = Member
        fields = ['nickname', 'discord_id', 'status', 'payment_method', 'paid_at']
        labels = {
            'nickname': _('nickname'),
            'discord_id': _('ID do Discord'),
            'status': _('Status'),
            'payment_method': _('Forma de Pagamento'),
            'paid_at': _('Data do Pagamento'),
        }
        help_texts = {
            'discord_id': _('Insira o ID do Discord do membro.'),
            'paid_at': _('Deixe em branco se ainda não pagou.'),
        }
        error_messages = {
            'nickname': {
                'required': _('O apelido é obrigatório.'),
            },
            'discord_id': {
                'required': _('O ID do Discord é obrigatório.'),
                'unique': _('Já existe um membro com esse ID do Discord.'),
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = self.STATUS_CHOICES
        self.fields['payment_method'].choices = self.PAYMENT_CHOICES
        for name, field in self.fields.items():
            field.widget.attrs['class'] = 'form-control'
        self.fields['paid_at'].widget = forms.DateInput(
            attrs={
                'type': 'date',
                'class': 'form-control',
                'placeholder': _('Selecione a data'),
            }
        )

    def save(self, commit=True):
        instance = super().save(commit=False)
        from django.utils import timezone
        from datetime import timedelta
        if instance.status == 'active' and not instance.paid_at:
            instance.paid_at = timezone.now()
        if instance.status == 'active' and instance.paid_at and instance.payment_method:
            if instance.payment_method == 'weekly':
                instance.expired_in = instance.paid_at + timedelta(days=7)
            elif instance.payment_method == 'monthly':
                instance.expired_in = instance.paid_at + timedelta(days=30)
        if commit:
            instance.save()
        return instance
