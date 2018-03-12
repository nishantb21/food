# datak.py

## datak.ingredient(*query*)
Queries Nutritionix, by checking for best match amongst results provided by search predictor, and **returns** an object of type *NutritionixResponse* on a successful query

### parameters:  
- *query* - Ingredient/Dish being looked up on nutritionix (str)

### returns:
- *NutritionixResponse* object, on a successful query.
- *None*, on an unsuccessful query

## datak.leech(*for_file*,*folder*)
*for_file* is a file that contains a list of dishes, which are queried via **ingredient(*query*)** , and writes the nutritional information to a file

### parameters: 
- *for_file* - File containing list of queries that will be looked up on nutritionix
- *folder* - Directory in which files are to be written

### returns:
- None

## datak.NutritionixResponse:
* datak.NutritionixResponse.**name**  
Name of the item queried  
* datak.NutritionixResponse.**item_id**  
Nutritionix's internal id used to tag items
* datak.NutritionixResponse.**item_type**  
?
* datak.NutritionixResponse.**nutrition_data**  
Contains the nutritional information of the item queried


