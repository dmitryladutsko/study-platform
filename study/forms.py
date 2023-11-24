from django import forms
from accounts.forms import ProfileEditForm
from .models import Group, Subject, Lesson, Test, Question, Answer, LessonPhoto
from django.contrib.auth.models import User


class AdminProfileEditForm(ProfileEditForm):

    def __init__(self, *args, **kwargs):
        super(ProfileEditForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'

        self.fields['group'] = forms.ModelChoiceField(
            queryset=Group.objects.all(),
            label='Группа',
        )
        self.fields['group'].required = False


class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ("name", )
        labels = {"name": "Название"}

    def __init__(self, *args, **kwargs):
        super(GroupForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'

        self.fields['owner'] = forms.ModelChoiceField(
            queryset=User.objects.filter(profile__type=2).all(),
            label='Владелец',
        )
        self.fields['owner'].required = False


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ("name", "group")
        labels = {"name": "Название", "group": "Группа"}

    def __init__(self, *args, **kwargs):
        super(SubjectForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class LessonForm(forms.ModelForm):
    class Meta:
        model = Lesson
        fields = ("name", "subject", "test", "video", "photos", "text")
        labels = {"name": "Название", "subject": "Предмет", "test": "Тест", "video": "Видео", "photos": "Фото", "text": "Текст"}

    def __init__(self, *args, **kwargs):
        super(LessonForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'

        self.fields["text"].widget.attrs['class'] = 'form__input full-w'


class TestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ["name"]
        labels = {"name": "Название"}

    def __init__(self, *args, **kwargs):
        super(TestForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class AdminTestForm(forms.ModelForm):
    class Meta:
        model = Test
        fields = ["name", "owner"]
        labels = {"name": "Название", "owner": "Владелец"}

    def __init__(self, *args, **kwargs):
        super(AdminTestForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'

        self.fields["owner"].queryset = self.fields["owner"].queryset.filter(profile__type=2)


class QuestionForm(forms.ModelForm):
    class Meta:
        model = Question
        fields = ("text", "type")
        labels = {"text": "Вопрос", "type": "Тип"}
        widgets = {"type": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(QuestionForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class AnswerForm(forms.ModelForm):
    class Meta:
        model = Answer
        fields = ("text", "correct")
        labels = {"text": "Ответ", "correct": ""}

    def __init__(self, *args, **kwargs):
        super(AnswerForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'


class LessonPhotoForm(forms.ModelForm):
    class Meta:
        model = LessonPhoto
        fields = ("name", "photo")
        labels = {"name": "Название", "photo": "Фото"}
        widgets = {"type": forms.RadioSelect}

    def __init__(self, *args, **kwargs):
        super(LessonPhotoForm, self).__init__(*args, **kwargs)

        for visible in self.visible_fields():
            visible.field.widget.attrs['class'] = 'form__input'
