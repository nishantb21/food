# Utilities.py

## utilities.modmatch(*query\_string, match\_string, threshold*)
Compares the *query_string* with the *match_string* by checking how similar they are.  


#### parameters :
 -  *query_string* - The string being queried
 -  *match_string* - The string being matched with
 -  *threshold* - The threshold for match to be successful

#### returns:
 - A tuple containing the *match_string* and the score of how similar the strings are if the score is greater than the *threshold*
 - *None* otherwise


## utilities.modmatchi(*query\_string, iterable, threshold*)
Compares the *query_string* with each element in the *iterable* and **returns** best possible match

#### parameters :
-  *query_string* - The string being queried
-  *iterable* - A list of *match_strings* 
-  *threshold* - The threshold for match to be successful

#### returns:
- Tuple containing best match and the percentage of match (*best_match*,*match_percentage*)

## utilities.modmatchir(*query\_string, nriterable, threshold*)
A variant of the **_modmatchi_** function, **returns** the index of the best match within the iterable.

#### parameters :
-  *query_string* - The string being queried
-  *nriterable* - A list of *match_strings* 
-  *threshold* - The threshold for match to be successful

#### returns:
- Index of best match if available, else -1.

## utilities.parameterize(*qstring*):
Replaces the spaces in query string with '+' and **returns**

#### parameters :
- qstring - Query string to be converted to a search query

#### returns:
- Cleaned up string. See below :

> parameterize("Key Lime Pie")  
> "Key+Lime+Pie


## utilities.hash(*input_title*)
Cleans the string, encodes into UTF-8 and **returns** an MD5 hash of the string

#### parameters :
- *input_title* - Dish name / String to be hashed
 
#### returns:
- MD5 hash of *input_title*

## utilities.package(*input_file*)
Reads through an *input_file* and generates a 1-depth trie tree file.
Sorts every string in the file based on the first
character.

#### parameters :
- *input_file* - File containing strings to be packaged into trie tree file

#### returns:
- None

## utilities.standardize(*input_file*)
For every food item queried, a file is generated
This file is read and the scores are standardized, so that each dish's nutritional information corresponds to a 100g serving, and later outputted to another file

#### parameters :
- *input_file* - file containing dish nutritional information to be standardized

#### returns:
- None

## utilities.ratio(*i_no = 1*):
Not in use.
Based on number of ingredients (*i_no*) in a particular dish, a percentage list is generated.
For an n-ingredient dish, a fraction of the *i*th dish is added to the first ingredient, and a percentage list is generated
**returns** percentage list

#### parameters :
- *i_no* - Number of ingredients in dish, default is 1

#### returns:
- An iterable containing *i_no* elements whose values are corresponding percentages. See below

>utilities.ratio(5)  
>[40.0, 18.0, 16.0, 14.0, 12.0]