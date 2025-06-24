# products/forms.py

from django import forms

PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 21)] # От 1 до 20

class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(
        choices=PRODUCT_QUANTITY_CHOICES,
        coerce=int, # Преобразует выбранное значение в целое число
        widget=forms.Select(attrs={'class': 'form-control'}), # Добавляем простой класс для стилизации
        label="Количество"
    )
    override = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.HiddenInput # Скрытое поле, чтобы знать, заменяем ли количество или добавляем
    )