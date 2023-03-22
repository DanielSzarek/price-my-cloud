from django import forms
from bootstrap_modal_forms.forms import BSModalModelForm
from node import models as node_models


class NodeCreationForm(forms.Form):
    node_name = forms.CharField(max_length=255)
    time_of_processing = forms.DurationField()
    file_field = forms.FileField(
        widget=forms.ClearableFileInput(attrs={"multiple": True}), required=False
    )


class ComponentModelForm(BSModalModelForm):
    name = forms.CharField(label="Component name")
    type = forms.ModelChoiceField(
        label="Select type of component",
        queryset=node_models.ComponentType.objects.all().order_by("name"),
    )
    # duration_of_operating = forms.DurationField(label="Duration of component operating")
    hidden = forms.BooleanField(label="Hide component?", required=False)

    class Meta:
        model = node_models.Component
        fields = (
            "name",
            "type",
            "hidden",
            "duration_of_operating",
        )
