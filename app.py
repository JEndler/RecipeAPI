from flask import abort, jsonify, make_response, Flask 
#from recipeManager import getRecipes
import json

#so müssen die ingredients aussehen
test_ingredient_list = {"ingredients":['möhre', 'gurke', 'lmao']}

app = Flask(__name__)

@app.route('/api/<string:ingredient_list>', methods=['GET'])
def get_task(ingredient_list):
	try:
		assert ";" in ingredient_list, "No valid input"
		data  = ingredient_list.split(";")
		print(data)
	except Exception as e:
		print(e)
		print("Invalid Input")
		abort(404)
	ingredient_list = data
	if len(ingredient_list) < 3:
		print("To few ingredients")
		abort(404)
	#recipe_data = getRecipes(ingredient_list)
	recipe_data = test_ingredient_list
	return jsonify(recipe_data)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Invalid Request'}), 404)

if __name__ == '__main__':
    app.run(debug=True, port=8027)
