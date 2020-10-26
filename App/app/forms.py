from datetime import datetime
from flask_wtf import Form
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField
from wtforms.validators import DataRequired, AnyOf, URL

class ProductForm(Form):
    name = StringField(
        'name', validators=[DataRequired()]
    )
    weight = StringField(
        'weight', validators=[DataRequired()]
    )
    quanitity = StringField(
        'quantity', validators=[DataRequired()]
    )
    date_purchased = DateTimeField(
        'date_purchased', validators=[DataRequired()]
    )
    image_link = StringField(
        'image_link'
    )


class UserForm(Form):
    first_name = StringField(
        'first_name', validators=[DataRequired()]
    )
    last_name = StringField(
        'last_name', validators=[DataRequired()]
    )
    age = StringField(
        'age', validators=[DataRequired()]
    )



