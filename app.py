from flask import abort, jsonify, make_response, Flask, render_template, request, redirect, url_for
from dbConnector import dbConnector
import json
from flask_wtf import FlaskForm
from wtforms import SubmitField, StringField
from wtforms.validators import Length, URL
from os import urandom

app = Flask(__name__,template_folder="templates")
app.config['SECRET_KEY'] = urandom(32)

class IngredientForm(FlaskForm):
    url = StringField('Ingredient', validators=[
        Length(max=1000, message='Maximum length exceeded!')])
    submit = SubmitField('Add Ingredient')

@app.route('/api/<string:ingredient_list>', methods=['GET'])
def get_task(ingredient_list):
	try:
		assert ";" in ingredient_list, "No valid input"
		data  = ingredient_list.split(";")
	except Exception as e:
		print(e)
		print("Invalid Input")
		abort(404)
	ingredient_list = data
	if len(ingredient_list) < 3:
		print("To few ingredients")
		abort(404)
	db = dbConnector()
	recipes = db.getRecipes(ingredient_list)
	return jsonify(recipes)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Invalid Request'}), 404)

# Make an entrypoint for the root domain of the app.
# This will contain a multiple input WTForm.
@app.route('/', methods=['GET', 'POST'])
def root():
	form = IngredientForm()
	if request.method == "POST" and form.validate_on_submit():
		return redirect(url_for('get_task', ingredient_list=form.url.data))
	return render_template('index.html', form=form)

if __name__ == '__main__':
    app.run(debug=True, port=8027)
