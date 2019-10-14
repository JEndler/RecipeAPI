from flask import abort
from recipeManager import getRecipes
import json

#so müssen die ingredients aussehen
test_ingredient_list = {"ingredients":['möhre', 'gurke', 'lmao']}

@app.route('/todo/api/v1.0/tasks/<str:json_arr>', methods=['GET'])
def get_task(json_arr):
	try:
		data  = json.loads(json_arr)
	except Exception as e:
		print("Invalid Json")
		abort(404)
	ingredient_list = data['ingredients']
	if len(ingredient_list) < 3: 
		print("To few ingredients")
		abort(404)
	recipe_data = getRecipes(ingredient_list)
    return jsonify(recipe_data=list)

@app.errorhandler(404)
def not_found(error):
    return make_response(jsonify({'error': 'Invalid Request'}), 404)

if __name__ == '__main__':
    app.run(debug=True)