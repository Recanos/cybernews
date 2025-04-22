from django import forms
from .models import Comment

class CommentForm(forms.ModelForm):
    parent_id = forms.IntegerField(widget=forms.HiddenInput(), required=False)
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'form-control',
                'placeholder': 'Введите ваш комментарий...',
                'label': '',
                'style': 'resize: none;'  # Запрещаем изменение размера
            }),
        }
        labels = {
            'content': ''
        } 