from django import forms


class NodeCreationForm(forms.Form):
    node_name = forms.CharField(max_length=255)
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )
