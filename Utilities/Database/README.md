# Database

To setup the database, make sure mongo service is running. Make sure pymongo is installed:
`pip install pymongo`

Then set up the new dataset like so:
`python setup_dataset.py`

The dataset now has normalized dish name e.g. "Mango lassi come here" becomes "mango lassi" (notice the lower case for the name). The nutrition facts for dishes have also been normalized. The format of the nutrional data is as follows:

`"nutrients": {
	"calories": [
		"102.77kcal",
		"0%"
	],
	"carbs": [
		"22.5g",
		"7%"
	],
	"cholesterol": null,
	"dietary_fiber": [
		"4.31g",
		"16%"
	],
	"fat": [
		"0.15g",
		"0%"
	],
	"protein": [
		"2.71g",
		"0%"
	],
	"sat_fat": [
		"0.02g",
		"0%"
	],
	"sodium": [
		"0.45g",
		"19%"
	],
	"sugar": [
		"13.92g",
		"0%"
	]
}`

The database is set up as the 'foodDatabase' database with the collection name as 'itemDetails'.