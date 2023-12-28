
multi_choice = [
("noise_day", "How much noise from the street and the rest of the house can you hear from your room in the day?", 
    ["Quiet", "Occasional noise", "Constant noise"]),
("noise_night", "How often does noise at night get loud enough to disturb someone's sleep?",
    ["Never", "Rarely", "Occasionally", "Frequently"]),
("temperature", "What is the temperature like in your room?",
    ["Comfortable (easily adjusted with windows and radiator)",
     "Too warm (even with windows open and heating off)",
     "Too cold (even with heating)"]),
("daylight", "How much natural light does your room get on an average day?", 
    ["Little (need lights on for reading or writing)",
     "Normal",
     "A lot (due to extra large windows, facing the sun, etc)"]),
("storage", "How much storage space is there?", 
    ["Less than standard",
    "Standard (wardrobe, chest of drawers, desk and bedside table drawers)",
    "More than standard",]),
("gyp_facilities", "What facilities are there in the kitchen/gyp you normally use?",
    ["Kettle, toaster, microwave. Enough to make a snack but not a proper meal.",
    "There is a hob but it doesnâ\x80\x99t work very well.",
    "There is a hob that works well.",
    "There is more than one hob or other extra appliances.",
    ]),
("gyp_cupboard", "How much cupboard space is there in the kitchen/gyp you normally use?", 
    ["Less than standard", "Standard (one cupboard per person)", "More than standard"]),
("bike_storage", "Is there a secure space for storing bicycles near your building?", 
    ["No, there isnât (chained to railings or street side stands).",
     "Yes, there is dedicated space but is easily accessed by the public (not secure).",
     "Yes, there is a shed or a private yard (e.g. SPT, WSB)."
     ]),
    # view and condition are sql reserved words
("room_view", "How would you describe the view from your window?", 
    [
        "Not ideal (basement, yard, wall-facing, etc)",
        "Standard (street, college court or other buildings)",
        "Scenic (greenery, church tower, horizon, etc)",
    ]),
("room_condition", "How would you describe the general state of the furnishings in your room?", 
    [
        "Run down (squeaky floor, drafty window, many marks on wall and furniture or peeling paint)",
        "Standard (minor damage from age but not significant)",
        "Excellent (recently refurbished in the last 5 years or so)",
    ]),
("laundry", "How far is the nearest washing machine you can use?", 
    [
        "In the same building",
        "In a different building but close by",
        "More than a building or two away",
    ]),
]
# previously these were shown as one through five
numerical = [
("n_gyp", "Roughly how many people (including you) share the kitchen/gyp you normally use?", ),
("n_shower", "Roughly how many people (including you) share the shower you normally use? (if your room is en-suite, put 0)", ),
("n_toilet", "Roughly how many people (including you) share the toilet you normally use? (if your room is en-suite, put 0)", )
]

q_by_q = {b: (a, c) for a,b,c in multi_choice}
q_by_q_numeric = {b: a for a,b in numerical}

def long_question(q_name):
    for n, q, a in multi_choice:
        if n == q_name:
            return q

    for n, q in numeric:
        if n == q_name:
            return q
