import json
import pickle
import sys
import os

my_path = os.path.abspath(os.path.dirname(__file__))

tags = {"sushi": ["non vegetarian", "sushi"], "milkshake": ["beverage", "milkshake"], "curried green bean salad": ["vegetarian", "salad", "bean"], "fried rice": ["vegetarian", "fried rice"], "salad": ["salad"], "green bean": ["vegetarian", "bean"], "keema aloo": ["non vegetarian", "beef", "curry", "potato"], "keema": ["non vegetarian", "keema"], "roti": ["roti"], "black chana with potato": ["vegetarian", "chana", "black chana", "potato"], "potato": ["vegetarian", "potato"], "chana": ["vegetarian", "chana"], "tomato cucumber kachumbar": ["vegetarian", "salad", "tomato", "cucumber"], "tomato": ["vegetarian", "tomato"], "cucumber": ["vegetarian", "cucumber"], "red split lentils": ["vegetarian", "lentil"], "lentil": ["vegetarian", "lentil"], "coconut chutney": ["vegetarian", "chutney", "coconut"], "coconut": ["vegetarian", "coconut"], "chutney": ["vegetarian", "chutney"], "fish": ["non vegetarian", "fish"], "chicken": ["non vegetarian", "chicken"], "shrimp": ["non vegetarian", "shrimp"], "pork": ["non vegetarian", "pork"], "tamarind sauce fish curry": ["non vegetarian", "fish", "curry", "tamarind"], "lamb": ["non vegetarian", "lamb"], "kashmiri lamb": ["non vegetarian", "lamb", "curry"], "chicken tikka masala": ["non vegetarian", "chicken", "curry", "tikka masala"], "naan": ["naan"], "soup": ["soup"], "mulligatawny soup": ["non vegetarian", "chicken", "soup"], "korma": ["vegetarian", "curry"], "curry": ["curry"], "gravy": ["curry"], "vegetarian korma": ["vegetarian", "curry"], "chicken curry": ["non vegetarian", "chicken", "curry"], "chicken makhani": ["non vegetarian", "chicken", "curry"], "red lentil curry": ["vegetarian", "curry", "lentil"], "butter chicken" :["non vegetarian", "chicken", "curry"], "vegan potato curry": ["vegan", "curry", "potato"], "carrot": ["vegetarian", "carrot"], "carrot rice": ["vegetarian", "rice", "carrot"], "chickpea curry": ["vegetarian", "curry", "chickpea"], "chickpea": ["vegetarian", "chickpea"], "baingan": ["vegetarian", "eggplant"], "aloo": ["vegetarian", "potato"], "gajar": ["vegetarian", "carrot"], "okra": ["vegetarian", "okra"], "bhindi": ["vegetarian", "okra"], "baingan bharta": ["vegetarian", "curry", "eggplant"], "eggplant curry": ["vegetarian", "curry", "eggplant"], "aloo phujia": ["vegetarian", "snack", "potato"], "tandoori chicken": ["non vegetarian", "chicken", "tandoori"], "basmati rice": ["vegetarian", "rice"], "chicken korma": ["non vegetarian", "chicken", "curry"], "tomato chicken": ["non vegetarian", "chicken", "curry", "tomato"], "mango": ["mango"], "lassi": ["beverage", "lassi"], "paneer": ["paneer"], "mango lassi": ["beverage", "lassi", "mango"], "palak paneer": ["vegetarian", "curry", "palak", "paneer"], "dahl": ["vegetarian", "dahl"], "dahl with spinach": ["vegetarian", "dahl", "spinach"], "beef": ["non vegetarian", "beef"], "samosa": ["snack", "samosa"], "beef samosas": ["non vegetarian", "beef", "snack", "samosa"], "chicken curry": ["non vegetarian", "chicken", "curry"], "masoor dal": ["vegetarian", "dal", "red lentil"], "dal" : ["vegetarian", "dal"], "masoor daal": ["vegetarian", "curry", "red lentil"], "chicken and mango curry": ["non vegetarian", "chicken", "curry", "mango"], "shrimp curry": ["non vegetarian", "shrimp", "curry"], "gobi": ["vegetarian", "gobi"], "gobi aloo": ["vegetarian", "potato", "gobi"], "coconut": ["vegetarian", "coconut"], "tofu": ["vegetarian", "tofu"], "coconut tofu keema": ["vegetarian", "curry", "coconut", "tofu"], "chapati": ["chapati"], "kheer": ["sweet dish"], "fish curry": ["non vegetarian", "fish", "curry"], "garam masala": ["masala"], "chicken stew with coconut milk": ["non vegetarian", "chicken", "curry", "coconut"], "bhindi masala": ["vegetarian", "curry", "okra"], "okra curry": ["vegetarian", "curry", "okra"], "saffron rice": ["vegetarian", "rice"], "rice": ["rice"], "chicken biryani": ["non vegetarian", "chicken", "biryani"], "chicken biriyani": ["non vegetarian", "chicken", "biryani"], "dahl": ["vegetarian", "dahl"], "cauliflower": ["vegetarian", "cauliflower"], "broccoli": ["vegetarian", "broccoli"], "cauliflower and broccoli soup": ["vegetarian", "curry", "cauliflower", "broccoli"], "navaratan korma": ["vegetarian", "curry"], "matar": ["vegetarian", "peas"], "peas": ["vegetarian", "peas"], "pulao": ["vegetarian", "rice"], "aloo matar": ["vegetarian", "curry", "potato", "peas"], "chicken and brown rice casserole": ["non vegetarian", "chicken", "rice"], "cucumber raita": ["vegetarian", "raita", "cucumber"], "sheekh kabab": ["non vegetarian", "lamb", "kebab"], "kulfi": ["dessert", "kulfi"], "coconut curry": ["vegetarian", "curry", "coconut"], "relish": ["condiment"], "shrimp curry": ["non vegetarian", "shrimp", "curry"], "potato curry": ["vegetarian", "curry", "potato"], "chana masala": ["vegetarian", "curry", "chana"], "apricot chicken": ["non vegetarian", "chicken", "apricot"], "cod curry": ["non vegetarian", "fish", "curry"], "coconut rice": ["vegetarian", "rice", "coconut"], "chickpea curry with turnip": ["vegetarian", "curry", "chickpea", "turnip"], "turnip": ["vegetarian", "turnip"], "pakora": ["snack", "pakora"], "vegetable pakora": ["vegetarian", "snack", "pakora"], "barley pilaf": ["non vegetarian", "chicken", "rice", "barley"], "cumin potatoes": ["vegetarian", "curry", "cumin", "potato"], "vegetable masala": ["vegetarian", "curry", "mixed vegetables"], "coconut curry": ["vegetarian", "curry", "coconut"], "curried cauliflower": ["vegetarian", "curry", "cauliflower"], "saag": ["vegetarian", "curry"], "coconut curry fish": ["non vegetarian", "fish", "curry", "coconut"], "cholay": ["vegetarian", "curry", "chickpea"], "peanut stew": ["vegan", "stew", "peanut"], "butter lamb gravy": ["non vegetarian", "lamb", "curry"], "saag paneer": ["vegetarian", "curry", "paneer"], "chole saag": ["vegetarian", "curry", "chole"], "green bean curry": ["vegetarian", "curry", "bean"], "tofu vindaloo": ["vegetarian", "curry", "tofu"], "chicken and rice": ["non vegetarian", "chicken", "rice"], "sweet potato": ["vegetarian", "sweet potato"], "sweet potato salad": ["vegetarian", "salad", "sweet potato"], "pork loin": ["non vegetarian", "pork"], "salmon fillets": ["non vegetarian", "fish", "salmon", "fillets"], "salmon": ["non vegetarian", "fish", "salmon"], "palak paneer": ["vegetarian", "curry", "paneer", "paneer"], "roomali roti": ["roti"], "vegetable rice": ["vegetarian", "rice", "mixed vegetables"], "chicken curry with potatoes": ["non vegetarian", "chicken", "curry", "potato"], "tandoori fish": ["non vegetarian", "fish", "tandoori"], "channa masala": ["vegetarian", "curry", "chana"], "pumpkin": ["vegetarian", "pumpkin"], "pumpkin curry with lentils": ["vegetarian", "curry", "pumpkin", "lentil"], "pumpkin curry": ["vegetarian", "curry", "pumpkin"], "curried chicken with couscous": ["non vegetarian", "chicken", "couscous"], "roasted chickpeas": ["vegetarian", "chickpea"], "chicken saag": ["non vegetarian", "chicken", "curry"], "cauliflower adn tofu masala": ["vegetarian", "curry", "cauliflower", "tofu"], "chicken and rice salad": ["non vegetarian", "chicken", "salad", "rice"], "maharaja curry": ["non vegetarian", "chicken", "curry"], "peach": ["peach"], "peach chutney": ["vegetarian", "chutney", "peach"], "kidney beans with turnips": ["vegetarian", "bean", "turnip"], "chicken hariyali tikka": ["non vegetarian", "chicken", "tikka"], "chicken curry with quinoa": ["non vegetarian", "chicken", "curry", "quinoa"], "lamb madras curry": ["non vegetarian", "lamb", "curry"], "haldi ka doodh": ["beverage"], "aloo gobi masala": ["vegetarian", "curry", "potato", "gobi"], "cucumber peanut salad": ["vegetarian", "salad", "cucumber", "peanut"], "roasted grapes and carrots": ["grape", "carrot"], "strawberry lassi": ["beverage", "lassi", "strawberry"], "beef and spinach curry": ["non vegetarian", "beef", "curry", "spinach"], "apple chutney": ["vegetarian", "chutney", "apple"], "shahi paneer": ["vegetarian", "vegetarian", "curry"], "green chutney": ["vegetarian", "chutney"], "bunjal chicken": ["non vegetarian", "chicken", "curry"], "vegetable bhaji": ["vegetarian", "bhaji", "mixed vegetables"], "lentil dip": ["condiment"], "chicken and potatoes": ["non vegetarian", "chicken", "curry", "potato"], "rajma": ["vegetarian", "curry", "kidney bean"], "sweet and spicy curry with chickpeas": ["non vegetarian", "turkey", "curry", "chickpea"], "turkey": ["non vegetarian", "turkey"], "dal makhani": ["vegetarian", "dal"], "gulab jamun": ["sweet dish"], "jalapeno pesto with lime": ["condiment"], "curry powder": ["masala"], "red kidney bean": ["vegetarian", "curry", "kidney bean"], "nariyal burfi": ["sweet dish"], "tamarind chutney": ["vegetarian", "chutney"], "pork chops": ["non vegetarian", "pork"], "hot curried mangoes with tofu": ["vegetarian", "curry", "mango", "tofu"], "pineapple lime and ginger soup": ["vegetarian", "soup", "pineapple", "ginger"], "pineapple": ["pineapple"], "jeera fried rice": ["vegetarian", "fried rice"], "jeera rice": ["vegetarian", "rice"], "ghee rice": ["vegetarian", "rice"], "sweet potato and lentil soup": ["vegetarian", "soup", "sweet potato", "lentil"], "spiced rice": ["vegetarian", "rice"], "blue ribbon curry chicken": ["non vegetarian", "chicken", "curry", "apple"], "spinach and cauliflower bhaji": ["vegetarian", "bhaji", "spinach", "cauliflower"], "carrot and peanut salad": ["vegetarian", "salad", "carrot", "peanut"], "exotic brinjal": ["vegetarian", "curry", "eggplant"], "barbeque chicken": ["non vegetarian", "chicken", "barbeque"], "mango-pineapple chutney": ["vegetarian", "chutney", "mango", "pineapple"], "beef vindaloo": ["non vegetarian", "beef", "curry"], "chicken saag": ["non vegetarian", "chicken", "curry"], "tomato lentil soup": ["vegetarian", "soup", "lentil", "tomato"], "vegetable biryani": ["vegetarian", "biryani"], "chicken curry": ["non vegetarian", "chicken", "curry"], "chicken vindaloo": ["non vegetarian", "chicken", "curry"], "pav bhaji": ["vegetarian", "pav bhaji"], "curried peas": ["vegetarian", "curry", "peas"], "coconut curry cabbage": ["vegetarian", "curry", "coconut", "cabbage"], "butter chicken": ["non vegetarian", "chicken", "curry"], "peanut rice": ["vegetarian", "rice", "peanut"], "carrot soup": ["vegetarian", "soup", "carrot"], "lamb biryani": ["non vegetarian", "lamb", "biryani"], "curried corn": ["vegetarian", "curry", "corn"], "corn": ["vegetarian", "corn"], "tofu curry salad": ["vegetarian", "salad", "tofu"], "curried lamb": ["non vegetarian", "lamb", "curry"], "tofu masala": ["vegetarian", "curry", "tofu"], "quinoa biryani": ["vegetarian", "biryani", "quinoa"], "garlic chicken": ["non vegetarian", "chicken", "curry", "garlic"], "salmon fry": ["non vegetarian", "fish", "salmon"], "kedgeree": ["non vegetarian", "fish", "rice", "egg"], "reshmi kebab": ["non vegetarian", "chicken", "kebab"], "cod fillets": ["non vegetarian", "fish", "cod", "fillets"], "paneer curry": ["vegetarian", "curry", "paneer"], "aloo gobhi": ["vegetarian", "curry", "potato", "gobi"], "black pepper goat curry": ["non vegetarian", "goat", "curry", "papper"], "kale and spinach saag": ["vegetarian", "curry", "kale", "spinach"], "spinach": ["vegetarian", "spinach"], "kale": ["vegetarian", "kale"], "besan halwa": ["sweet dish"], "lamb stew": ["non vegetarian", "lamb", "curry"], "masala beef with ginger and curry leaf": ["non vegetarian", "beef", "curry", "ginger"], "spinach and buttermilk soup": ["vegetarian", "soup", "spinach", "buttermilk"], "buttermilk": ["buttermilk"], "chicken wings": ["non vegetarian", "chicken"], "vendakka paalu": ["vegetarian", "curry", "okra", "coconut"], "ras malai": ["sweet dish"], "naan bread pizza": ["vegetarian", "pizza"], "paneer butter masala": ["vegetarian", "curry", "paneer"], "turnip with coconut": ["vegetarian", "curry", "turnip", "coconut"], "tomato chutney": ["vegetarian", "chutney", "tomato"], "coconut sevai": ["vegetarian", "vermicelli", "coconut"], "cilantro chutney chicken": ["non vegetarian", "chicken", "chutney", "cilantro"], "biryani": ["non vegetarian", "chicken", "biryani"], "biriyani": ["non vegetarian", "chicken", "biryani"], "green pea poulourie": ["vegetarian", "snack", "peas"], "turkey curry": ["non vegetarian", "turkey", "curry"], "burger": ["non vegetarian", "lamb", "burger"], "chicken fry": ["non vegetarian", "chicken", "saute"], "fish fry": ["non vegetarian", "fish", "saute"], "spicy swordfish": ["non vegetarian", "fish", "curry", "mango", "coconut"], "pork vindaloo": ["non vegetarian", "pork", "curry"], "seitan makhani": ["vegan", "curry", "wheat"], "chicken navaratan curry": ["navaratan vegetarian", "chicken", "curry"], "lamb vindaloo": ["non vegetarian", "lamb", "curry"], "fettuccine bombay": ["non vegetarian", "chicken", "pasta"], "fettuccine": ["pasta"], "vindaloo": ["curry"], "halibut": ["non vegetarian", "fish", "halibut"], "hash browns": ["vegetarian", "snack", "potato"], "paneer makhani": ["vegetarian", "curry", "paneer"], "sabji": ["vegetarian", "curry"], "subji": ["vegetarian", "curry"], "curry chicken": ["non vegetarian", "chicken", "curry"], "matar paneer": ["vegetarian", "curry", "peas", "paneer"], "chickpea salad": ["vegetarian", "salad", "chickpea", "pineapple", "carrot", "cucumber", "mango"], "vegetable curry": ["vegetarian", "curry", "mixed vegetables"], "lamb korma": ["non vegetarian", "lamb", "curry"], "egg salad": ["egg", "salad"], "egg": ["egg"], "scrambled egg": ["egg"], "omelet": ["egg"], "egg bhurji": ["egg", "salad"], "carrot-bean sprouts salad": ["vegetarian", "salad", "carrot", "bean"], "grilled chicken": ["non vegetarian", "chicken"], "mango mint lassi": ["beverage", "lassi", "mango", "mint"], "spicy shrimp": ["non vegetarian", "shrimp", "curry"], "paneer jalfrazie": ["vegetarian", "jalfrazie", "paneer"], "jalfrazie": ["non vegetarian", "jalfrazie"], "bangaladumpa": ["vegetarian", "curry", "potato"], "tomato soup": ["vegetarian", "soup", "tomato"], "prawns in cashew coconut curry": ["non vegetarian", "prawn", "curry", "cashew", "coconut"], "prawn": ["non vegetarian", "prawn"], "lentil kootu": ["vegetarian", "sambar", "lentil"], "kootu": ["vegetarian", "sambar"], "spinach and tomato dal": ["vegetarian", "dal", "spinach", "tomato"], "meat samosa": ["non vegetarian", "chicken", "samosa"], "pumpkin butter bean and spinach curry": ["vegetarian", "curry", "pumpkin", "spinach", "bean"], "lasooni murgh": ["non vegetarian", "chicken", "curry", "garlic"], "dosa": ["vegetarian", "dosa"], "masala dosa": ["vegetarian", "dosa", "potato"], "rava dosa": ["vegetarian", "dosa", "rava"], "onion dosa": ["vegetarian", "dosa", "onion"], "vegetable kofta": ["vegetarian", "kofta"], "malai kofta": ["vegetarian", "kofta"], "pumpkin soup": ["vegetarian", "soup", "pumpkin"], "carrot soup": ["vegetarian", "soup", "carrot"], "dahi batata puri": ["vegetarian", "chaat", "curd"], "bhel puri": ["vegetarian", "chaat"], "masala puri": ["vegetarian", "chaat"], "tikki puri": ["vegetarian", "chaat"], "sev puri": ["vegetarian", "chaat"], "dahi puri": ["vegetarian", "chaat", "curd"], "dahi": ["curd"], "sambar": ["vegetarian", "sambar"], "rice with raisins and cashews": ["vegetarian", "rice", "raisin", "cashew"], "prawn biryani": ["non vegetarian", "prawn", "biryani"], "cilantro chutney": ["vegetarian", "chutney", "cilantro"], "banana curry": ["vegetarian", "curry", "banana"], "moong dal with spinach": ["vegetarian", "dal", "spinach"], "upma": ["vegetarian", "upma"], "poha": ["vegetarian", "poha"], "chicken curry": ["non vegetarian", "chicken", "curry"], "tandoori masala": ["masala"], "bhuna gosht": ["non vegetarian", "mutton", "curry"], "mutton": ["non vegetarian", "mutton"], "batata nu shak": ["vegetarian", "curry", "potato"], "potato curry": ["vegetarian", "curry", "potato"], "aaloo": ["vegetarian", "potato"], "akki rotti": ["vegetarian", "roti", "rice"], "lamb chops": ["non vegetarian", "lamb"], "chicken vindaloo": ["non vegetarian", "chicken", "curry"], "tangy rice": ["vegetarian", "rice", "tamarind", "curry leaf"], "alu baigan": ["vegetarian", "curry", "potato", "eggplant"], "alu": ["vegetarian", "potato"], "brinjal": ["vegetarian", "eggplant"], "eggplant raita": ["vegetarian", "raita", "eggplant"], "potato cutlet": ["vegetarian", "snack", "cutlet", "potato"], "cutlet": ["snack", "cutlet"], "chicken cutlet": ["non vegetarian", "chicken", "snack", "cutlet"], "mustard fish": ["non vegetarian", "fish", "mustard"], "gobi masala": ["vegetarian", "curry", "gobi"], "coconut chutney": ["vegetarian", "chutney", "coconut"], "sarson ka saag": ["vegetarian", "curry"],"dip": ["condiment"], "aloo matar paneer": ["vegetarian", "curry", "paneer", "peas", "potato"], "egg curry": ["egg", "curry"], "banana lassi": ["beverage", "lassi", "banana"], "carrot salad": ["vegetarian", "salad", "carrot"], "frizzled onion": ["vegetarian", "snack", "onion"], "chickpea coconut salad": ["vegetarian", "salad", "chickpea", "coconut"], "sandwich": ["sandwich"], "sweet corn subji with paneer and cashew nuts": ["vegetarian", "curry", "sweet corn", "paneer", "cashew"], "sweet corn": ["vegetarian", "sweet corn"], "cabbage": ["vegetarian", "cabbage"], "aloo palak": ["vegetarian", "curry", "potato", "palak"], "grilled chicken salad": ["non vegetarian", "chicken", "salad"], "chicken salad": ["non vegetarian", "chicken", "salad"], "mushroom": ["vegetarian", "mushroom"], "italian burger": ["egg", "burger"], "besan ladoo": ["sweet dish"], "matar pulao": ["vegetarian", "rice", "peas"], "cabbage tomato onion salad": ["vegetarian", "salad", "cabbage", "tomato", "onion"], "curd rice": ["vegetarian", "rice", "curd"], "yoghurt": ["yogurt"], "yogurt": ["yogurt"], "prawn curry": ["non vegetarian", "prawn", "curry"], "pilau": ["pilau"], "quinoa pilau": ["vegetarian", "pilau", "quinoa"], "paneer tikka masala": ["vegetarian", "curry", "paneer"], "latke": ["vegetarian", "latke", "potato"], "coconut cilantro rice": ["vegetarian", "rice", "coconut", "cilantro"], "egg and potato currry": ["egg", "curry", "potato"], "noodles": ["noodles"], "edamame": ["vegetarian", "bean", "edamame"], "cucumber carrot salad": ["vegetarian", "salad", "cucumber", "carrot"], "besan laddu": ["sweet dish"], "ladoo": ["sweet dish"], "laddu": ["sweet dish"], "beetroot": ["vegetarian", "beetroot"], "sabudhana khichdi": ["vegetarian", "khichdi", "sabudana"], "sabudhana": ["vegetarian", "sabudana"], "sabudana": ["vegetarian", "sabudana"], "khichdi": ["vegetarian", "khichdi"], "eggplant yogurt salad": ["vegetarian", "salad", "eggplant", "yogurt"], "egg halwa": ["egg", "sweet dish"], "gosht": ["non vegetarian", "lamb"], "rasam": ["vegetarian", "rasam", "tomato"], "sundal": ["vegetarian", "snack", "sundal"], "rasgulla": ["sweet dish"], "adai": ["vegetarian", "dosa"], "zucchini": ["vegetarian", "zucchini"], "zucchini soup": ["vegetarian", "soup", "zucchini"], "lentil quinoa curry": ["vegetarian", "curry", "lentil", "quinoa"], "butternut coconut curry": ["vegetarian", "curry", "butternut", "coconut"], "khitchari": ["vegetarian", "rice", "bean"], "meatball": ["non vegetarian", "meatball"], "chicken burger": ["non vegetarian", "chicken", "burger"], "lentil samosa": ["vegetarian", "snack", "samosa", "lentil"], "dressing": ["dressing"], "apricot chutney": ["vegetarian", "chutney", "apricot"], "pesarattu": ["vegetarian", "dosa"], "murgh": ["non vegetarian", "chicken"], "pongal": ["vegetarian", "pongal"], "egg kulambu": ["egg", "curry"], "kulambu": ["curry"], "rabri": ["beverage"], "kadhi": ["vegetarian", "kadhi"], "bhath": ["vegetarian", "rice"], "makhani murgh": ["non vegetarian", "chicken", "curry"], "prawns curry": ["non vegetarian", "prawn", "curry"], "prawn curry": ["non vegetarian", "prawn", "curry"], "shrikhand": ["sweet dish"], "capsicum": ["vegetarian", "capsicum"], "capsicum zunka": ["vegetarian", "zunka", "capsicum"], "zunka": ["vegetarian", "zunka"], "kesari bhat": ["sweet dish"], "kesari bath": ["sweet dish"], "kesri bath": ["sweet dish"], "kesribath": ["sweet dish"], "kesaribath": ["sweet dish"], "rava laddu": ["sweet dish"], "sprouts": ["vegetarian", "sprouts"], "pancake": ["vegetarian", "pancake"], "paratha": ["paratha"], "aloo paratha": ["vegetarian", "paratha", "potato"], "gobi paratha": ["vegetarian", "paratha", "gobi"], "pudina chutney": ["vegetarian", "chutney", "mint"], "pudina": ["vegetarian", "mint"], "gasagage payasa": ["sweet dish"], "gasagase payasa": ["sweet dish"], "payasa": ["sweet dish"], "poori": ["vegetarian", "poori"], "pachadi": ["vegetarian", "pachadi", "curd"], "avial": ["vegetarian", "curry"], "aviyal": ["vegetarian", "curry"], "ginger soup": ["vegetarian", "soup", "ginger"], "pacchadi": ["vegetarian", "pachadi", "curd"], "machhere": ["non vegetarian", "fish"], "atta halwa": ["sweet dish"], "halwa": ["sweet dish"], "crepe": ["vegetarian", "crepe"], "pasta": ["pasta"], "goat": ["non vegetarian", "goat"], "goat biryani": ["non vegetarian", "goat", "biryani"], "pizza": ["pizza"], "celery": ["vegetarian", "celery"], "veg biryani": ["vegetarian", "rice", "mixed vegetables"], "sawine": ["sweet dish"], "shami kebab": ["non vegetarian", "chicken", "kebab"], "vegan turnip curry": ["vegan", "curry", "turnip"], "junka": ["vegetarian", "zunka"], "kadai chicken": ["non vegetarian", "chicken", "curry"], "goat curry": ["non vegetarian", "goat", "curry"], "watermelon chutney": ["vegetarian", "chutney", "watermelon"], "pakoda": ["snack", "pakora"], "corn pakoda": ["vegetarian", "snack", "pakoda", "corn"], "jackfruit curry": ["vegetarian", "curry", "jackfruit"], "prawn pulao": ["non vegetarian", "prawn", "rice"], "cabbage soup": ["vegetarian", "soup", "cabbage"], "thokku": ["condiment"], "pumpkin curry": ["vegetarian", "curry", "pumpkin"], "shahi tukray": ["sweet dish"], "pineapple chutney": ["vegetarian", "chutney", "pineapple"], "pork vindaloo": ["non vegetarian", "pork", "curry"], "green apple and coconut chutney": ["vegetarian", "chutney", "green apple", "coconut"], "garlic chutney": ["vegetarian", "chutney", "garlic"], "cranberry chutney": ["vegetarian", "chutney", "cranberry"], "pea salad": ["vegetarian", "salad", "peas"], "onion chutney": ["vegetarian", "chutney", "onion"], "mango chutney": ["vegetarian", "chutney", "mango"], "bread pudding": ["dessert"], "coconut curry chicken": ["non vegetarian", "chicken", "curry", "coconut"], "cumin lassi": ["beverage", "lassi", "cumin"], "peanut cilantro chutney": ["vegetarian", "chutney", "peanut", "cilantro"], "patholi": ["sweet dish"], "pulihora": ["vegetarian", "rice", "tamarind"], "kobbari annam": ["vegetarian", "rice", "coconut"], "podi": ["masala"], "mithai": ["sweet dish"], "kobbari louz": ["sweet dish"], "pappu": ["vegetarian", "dal"], "majjiga": ["beverage", "buttermilk"], "mousse": ["dessert"], "mullingi rasam": ["vegetarian", "rasam", "radish"], "peach salad": ["vegetarian", "salad", "peach"], "phaal": ["non vegetarian", "lamb", "curry"], "chicken phaal": ["non vegetarian", "chicken", "curry"], "dosai": ["vegetarian", "dosa"], "mutton varuval": ["non vegetarian", "mutton", "curry"], "carrot halwa": ["sweet dish"], "lemon rice": ["vegetarian", "rice", "lemon"], "lamb vindaloo": ["non vegetarian", "lamb", "curry"], "bonda": ["snack", "bonda"], "spaghetti": ["pasta"], "dum biryani": ["vegetarian", "biryani"], "subzi": ["vegetarian", "curry"], "bhindi subzi": ["vegetarian", "curry", "okra"], "kadai bhindi": ["vegetarian", "curry", "okra"], "la-jawab sabut bhindi": ["vegetarian", "curry", "okra"], "chili paneer": ["vegetarian", "paneer"], "matar paneer": ["vegetarian", "curry", "peas", "paneer"], "spinach & green pea patties": ["vegetarian", "snack", "kebab"], "lentil dal": ["vegetarian", "dal", "lentil"], "coconut chicken tikka masala": ["non vegetarian", "chicken", "curry", "coconut"], "tuna salad": ["non vegetarian", "fish", "tuna", "salad"], "almond burfi": ["sweet dish"], "holige": ["sweet dish"], "crab curry": ["non vegetarian", "crab", "curry"], "crab": ["non vegetarian", "crab"], "peanut chaat": ["vegetarian", "chaat"], "khandvi": ["vegetarian", "snack", "khandvi"], "pasta alfredo": ["vegetarian", "pasta"], "aloo beans": ["vegetarian", "curry", "potato", "bean"], "aloo bhindi": ["vegetarian", "curry", "potato", "okra"], "aloo methi": ["vegetarian", "potato", "methi"], "appam": ["vegetarian", "dosa", "coconut"], "baby corn manchurian": ["vegetarian", "manchurian", "baby corn"], "manchurian": ["manchurian"], "gobi manchurian": ["vegetarian", "manchurian", "gobi"], "bacon wraps": ["non vegetarian", "bacon"], "bacon": ["non vegetarian", "bacon"], "apple pie": ["dessert"], "pie": ["dessert"], "banana chips": ["vegetarian", "snack", "chips", "banana"], "bean salad": ["vegetarian", "salad", "bean"], "bisi bele bath": ["vegetarian", "bisi bele bath"], "oats": ["vegetarian", "oats"], "cake": ["dessert"], "cheesecake": ["dessert"], "broccoli soup": ["vegetarian", "soup", "broccoli"], "garlic fried rice": ["vegetarian", "fried rice", "garlic"], "cajun pasta": ["non vegetarian", "pasta"], "toetellini salad": ["vegetarian", "salad", "broccoli", "tomato"], "shrimp ceasar salad": ["non vegetarian", "shrimp", "salad"], "ceasar salad with chicken": ["non vegetarian", "chicken", "salad"], "chakli": ["vegetarian", "snack", "chakli"], "murukku": ["vegetarian", "snack", "chakli"], "chicken cheese ball": ["non vegetarian", "chicken", "snack", "cheese ball"], "cheese ball": ["vegetarian", "snack", "cheese ball"], "cheese burger": ["non vegetarian", "beef", "burger"], "bacon cheese burger": ["non vegetarian", "bacon", "burger"], "fondue": ["dessert"], "bacon cheese fries": ["non vegetarian", "bacon", "fries"], "chicken burger": ["non vegetarian", "chicken", "burger"], "chicken fried rice": ["non vegetarian", "chicken", "fried rice"], "chicken frittata": ["non vegetarian", "chicken", "frittata"], "frittata": ["egg", "frittata"], "lasagne": ["lasagne"], "chicken lasagne": ["non vegetarian", "chicken", "lasagne"], "chicken manchurian": ["non vegetarian", "chicken", "manchurian"], "chicken momo": ["non vegetarian", "chicken", "momo"], "momo": ["momo"], "chicken noodles": ["non vegetarian", "chicken", "noodles"], "lemon chicken pasta": ["non vegetarian", "pasta", "chicken", "lemon"], "chicken pizza": ["non vegetarian", "chicken", "pizza"], "sausage": ["non vegetarian", "pork", "sausage"], "chicken sausage": ["non vegetarian", "chicken", "sausage"], "chicken shawarma": ["non vegetarian", "chicken", "shawarma"], "chicken soup": ["non vegetarian", "chicken", "soup"], "spring roll": ["vegetarian", "spring roll"], "chicken spring roll": ["non vegetarian", "chicken", "spring roll"], "tart": ["dessert"], "chickpea burger": ["vegetarian", "burger", "chickpea"], "chilli paneer": ["vegetarian", "paneer"], "honey chilli potatoes": ["vegetarian", "potato", "honey"], "brownie": ["dessert"], "chocolate milkshake": ["beverage", "milkshake", "chocolate"], "vanilla milkshake": ["beverage", "milkshake", "vanilla"], "strawberry milkshake": ["beverage", "milkshake", "strawberry"], "bhatura": ["vegetarian", "bhatura"], "chopsuey": ["non vegetarian", "chicken", "chopsuey"], "chowmein": ["vegetarian", "chowmein"], "egg chowmein": ["egg", "chowmein"], "chundal": ["vegetarian", "snack", "sundal"], "corn palak": ["vegetarian", "curry", "corn", "palak"], "baby corn palak": ["vegetarian", "baby corn", "palak"], "palak soup": ["vegetarian", "soup", "palak"], "corn salad": ["vegetarian", "salad", "corn"], "capsicum masala": ["vegetarian", "curry", "capsicum"], "vada": ["vegetarian", "vada"], "dahi vada": ["vegetarian", "vada", "curd"], "dahi bhalla": ["vegetarian", "chaat", "curd"], "methi dal": ["vegetarian", "dal", "methi"], "dal tadka": ["vegetarian", "dal"], "tadka dal": ["vegetarian", "dal"], "idli": ["vegetarian", "idli"], "idly": ["vegetarian", "idli"], "dhokla": ["vegetarian", "snack", "dhokla"], "donut": ["dessert"], "mushroom rice": ["vegetarian", "rice", "mushroom"], "dum aloo": ["vegetarian", "curry", "potato"], "egg roll": ["egg"], "egg sandwich": ["egg", "sandwich"], "ice cream": ["dessert"], "falooda": ["dessert"], "fish curry": ["non vegetarian", "fish", "curry"], "french fries": ["vegetarian", "snack", "fries"], "french toast": ["egg", "sandwich"], "smoothie": ["beverage", "smoothie"], "fruit bowl": ["vegetarian", "salad", "fruits"], "fruit salad": ["vegetarian", "salad", "fruits"], "gajar matar": ["vegetarian", "curry", "carrot", "peas"], "aloo gajar matar": ["vegetarian", "potato", "carrot", "peas"], "aloo gobi matar": ["vegetarian", "potato", "gobi", "peas"], "greek salad": ["vegetarian", "salad"], "hashbrown": ["vegetarian", "snack", "potato"], "cinnamon": ["cinnamon"], "pickle": ["condiment"], "jalebi": ["sweet dish"], "kachori": ["vegetarian", "snack", "kachori"], "kadhai chicken": ["non vegetarian", "chicken", "curry"], "kadhai paneer": ["vegetarian", "curry", "paneer"], "kaju katli": ["sweet dish"], "karela": ["vegetarian", "bitter gourd"], "bitter gourd": ["vegetarian", "bitter gourd"], "bitter gourd recipe": ["vegetarian", "curry", "bitter gourd"], "karela sabzi": ["vegetarian", "curry", "bitter gourd"], "khakhra": ["vegetarian", "snack", "khakhra"], "misal pav": ["vegetarian", "misal pav"], "kulcha": ["roti"], "lamb biryani": ["non vegetarian", "lamb", "biryani"], "lamb burger": ["non vegetarian", "lamb", "burger"], "paneer dosa": ["vegetarian", "dosa", "paneer"], "paneer masala dosa": ["vegetarian", "dosa", "paneer", "potato"], "papad": ["vegetarian", "snack", "papad"], "matar paneer": ["vegetarian", "curry", "paneer", "peas"], "methi matar": ["vegetarian", "curry", "methi", "peas"], "methi paratha": ["vegetarian", "paratha", "methi"], "mooli paratha": ["vegetarian", "paratha", "radish"], "mozzarella sticks": ["vegetarian", "snack"], "mushroom pizza": ["vegetarian", "pizza", "mushroom"], "mutton biryani": ["non vegetarian", "mutton", "biryani"], "nachos": ["vegetarian", "snack", "nachos"], "neer dosa": ["vegetarian", "dosa"], "onion paratha": ["vegetarian", "paratha" ,"onion"], "palak paratha": ["vegetarian", "paratha", "palak"], "paneer bhurji": ["vegetarian", "paneer"], "pani puri": ["vegetarian", "chaat"], "popcorn": ["vegetarian", "snack", "popcorn"], "lasagna": ["lasagne"], "pork tacos": ["non vegetarian", "pork", "tacos"], "taco": ["vegetarian", "taco"], "burrito": ["vegetarian", "burrito"], "potato wedges": ["vegetarian", "snack", "potato"], "pudina paratha": ["vegetarian", "paratha", "mint"], "puran poli": ["sweet dish"], "ragi ball": ["vegetarian", "ragi ball"], "ragi mudde": ["vegetarian", "ragi ball"], "rasgula": ["sweet dish"], "rava idli": ["vegetarian", "idli"], "ravioli": ["vegetarian", "pasta"], "waffle": ["egg", "waffle"], "hummus": ["condiment"], "chicken taco": ["non vegetarian", "chicken", "taco"], "quesadilla": [ "quesadilla"], "chicken quesadilla": ["non vegetarian", "chicken", "quesadilla"], "veg puff": ["vegetarian", "snack"], "fajita": ["non vegetarian", "fajita"], "chicken fajita": ["non vegetarian", "chicken", "fajita"], "vangibath": ["vegetarian", "rice", "eggplant"], "vangi bath": ["vegetarian", "rice", "eggplant"], "vada pav": ["vegetarian", "snack", "vada pav"], "tiramisu": ["dessert"], "thepla": ["vegetarian", "thepla", "paratha"], "methi thepla": ["vegetarian", "thepla", "paratha", "methi"], "ham": ["non vegetarian", "ham"], "papdi chat": ["vegetarian", "chaat", "curd"], "papdi chaat": ["vegetarian", "chaat", "curd"]}

def set_tags():
	data = json.load(open(os.path.join(my_path,"../Utilities/itemdetails.json")))

	veg_non_veg = {'non vegetarian', 'vegetarian'}

	final_dict = {}

	for i in data:
		dishName = i["dish_name"].lower()
		ingredients = i["ingredients"]

		t = []

		if dishName in tags:
			t.extend(tags[dishName])

		for j in dishName.split():
			if j in tags:
				if tags[j] not in t:
					t.extend(tags[j])

		for j in tags:
			if j in dishName:
				if tags[j] not in t:
					t.extend(tags[j])

		for j in ingredients:
			for k in j.lower().split():
				if k in tags:
					t.extend(tags[k])

		non_veg = 0
		t = set(t)
		if 'non vegetarian' in t:
			non_veg = 1
		t = t - veg_non_veg

		final_dict[dishName] = (sorted(set(t)), non_veg)

	pickle.dump(final_dict, open(os.path.join(my_path,"../Utilities/Team 2/tagged_dishes.pickle"), 'wb'))
	return final_dict

def get_tags_as_dict(final_dict, dishName):
	"""
	Input - 
	final_dict : A dictionary of tagged dishes
	dishName : dish that needs to be tagged

	Output -
	dictionary of the form {tag1 : 1, tag2 : 1, ...}
	"""
	dishName = dishName.lower()
	to_return = {}
	if dishName in final_dict:
		tags = final_dict[dishName]
		for i in tags[0]:
			to_return[i] = 1
		return to_return 

def all_unique_tags():
	"""
	Read the tags datbase and return a list of unique values

	Output -
	List of unique values in the tags database
	"""
	all_tags = []
	for i in tags:
		all_tags.extend(tags[i])

	all_tags = list(set(all_tags))

	return all_tags

def get_difference(all_tags, tags):
	to_add = set(all_tags) - set(tags)
	for i in to_add:
		tags[i] = 0

	return tags

# def sorted_tags(dishName, all_tags):
# 	tags = get_tags(dishName)[0]

# 	x = np.zeros(shape = (1, len(all_tags))
# 	for i in tags:
# 		if i in all_tags:


if __name__ == "__main__":
	# result = set_tags()
	# print(result)
	all_unique_sorted_tags()