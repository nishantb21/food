# layer1.py

## layer1.get\_data\_from\_JSON(*food_item*)

**returns** nutritional information of *food_item* if corresponding JSON file exists.

#### parameters:
 - *food_item* - Dish to be queried

#### returns:
 - JSON object containing nutritional information of *food_item*
 - *None* ,if not found

## layer1.write\_data\_to\_JSON(*food_item*, *nutri\_info*)
Hashes *food_item* (*see utilities.hash()*) creates JSON file populating it with its nutritional information (*nutri_info*)

#### parameters:
- *food_item* - Dish being written
- *nutri\_info* - JSON object containing nutritional information of dish


#### returns:
- *None*

## layer1.query\_JSON(*food_item*)
**returns** nutritional information of *food_item* if an exact match for JSON file is found 
Else, tries to find closest match and **returns** *nutri_info* after reading from JSON  
Else, **returns** *None*

#### parameters:
- *food_item* - Dish being queried

#### returns:
- JSON object containing nutritional information of dish, read from corresponding file
- *None*, if not found

## layer1.query\_nutritionix(*food_item*)
Since food item wasn't found in local storage, queries *food_item* to nutritionix and **returns** a result, and writes it to a file so it can be accessed 

#### parameters:
- *food_item* - Dish being queried, via Nutritionix

#### returns:
- *None*

## layer1.return_score(*food_item*)
**returns** nutritional information of queried *food_item* by:  

* Checking for JSON file (see: *query_JSON*)  
* Querying Nutritionix (see: *query_nutritionix*)
* **returns** *None*

#### parameters:
- *food_item* - Dish being queried, via Nutritionix

#### returns:
- JSON object containing nutritional information of dish, read from corresponding file
- *None*, if not found


##
