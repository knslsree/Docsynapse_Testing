from flask import Flask, render_template, request, flash, redirect, url_for
from flask_wtf import FlaskForm, CSRFProtect
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-super-secret-key-change-in-production'

# Initialize CSRF protection globally across the app
csrf = CSRFProtect(app)

# Define a Form using Flask-WTF which automatically manages CSRF tokens
class UpdateProfileForm(FlaskForm):
    username = StringField('New Username', validators=[DataRequired()])
    submit = SubmitField('Update Profile')

@app.route('/', methods=['GET', 'POST'])
def index():
    form = UpdateProfileForm()
    
    if request.method == 'POST':
        # validate_on_submit() automatically checks if the CSRF token is valid
        if form.validate_on_submit():
            new_username = form.username.data
            flash(f'Success! Profile updated to: {new_username}', 'success')
            return redirect(url_for('index'))
        else:
            flash('CSRF token validation failed or invalid input!', 'danger')
            
    return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True)