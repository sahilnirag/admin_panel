"""
User Roles
"""
USER_ROLE = ((1,"Super_Admin"),(2,"Customer"),(3,"Company"))

SUPER_ADMIN = 1
CUSTOMER = 2
COMPANY = 3 

"""
User Status
"""
USER_STATUS = ((1,"Active"),(2,"Inactive"),(3,"Deleted"))

ACTIVE = 1
INACTIVE = 2
DELETED = 3

"""
API Pagination
"""
API_PAGINATION = 10

"""
Plans Type
"""
SUBSCRIPTION_PLAN = ((1,"Basic Plan"),(2,"Enterprise"),(3,"Advance Plan"))

BASIC_PLAN = 1
ENTERPRISE = 2
ADVANCE_PLAN = 3


"""
Device
"""
DEVICE_TYPE  = ((1,"Android"),(2,"IOS"),)
ANDROID = 1
IOS = 2



EYE_CHOICES = [('left', 'Left Eye'),('right', 'Right Eye'),]
VISION_TEST_CHOICES = [('myopia', 'Myopia Test'),('hyperopia', 'Hyperopia Test'),('presbyopia', 'Presbyopia Test'),]


"""
Payment Modes
"""
PAYMENT_MODES = ((1,"Strip"),(2,"Other"))

STRIPE = 1
OTHER = 2

"""
PayMod
"""

PAYMOD = ((1,"Prepaid"),(2,"Postpaid"))

PREPAID = 1
POSTPAID = 2


PAYMENT_TYPE = ((1,'Payment'),(2,'Refund'))
PAYMENT = 1
REFUND = 2


"""
demi object for customer

"""

CUSTOMER_DATA = [
            {
                "domain_url":"zukti.localhost",
                "name": "John Doe",
                "age": 32
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Jane Smith",
                "age": 21
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Bob Johnson",
                "age": 26
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Alice Brown",
                "age": 28
            },
            {
                "domain_url":"zukti.localhost",
                "name": "swilson",
                "age": 41
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Eva Davis",
                "age": 22
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Mike Miller",
                "age": 34
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Sara White",
                "age": 27
            },
            {
                "domain_url":"zukti.localhost",
                "name": "Tom Green",
                "age": 33
            },
            {
                "domain_url":"zukti.localhost",
                "name": "rohit",
                "age": 31
            }
    ]

#### Eyetest constant ##########
NUMBER_OF_LETTER=(
    ('one', 'One Letter'),
    ('three', 'Three Letter'),
    ('four', 'Four Letter'),
    ('five', 'five Letter'),
)

CHOOSE_ASTIGMATISM = (
    ('a', 'A'),
    ('b', 'B'),
    ('c', 'C'),
    ('d', 'D'),
)
QUESTION_CONSTANT = {
    "ONE": 1,
    "TWO": 2,
    "THREE": 3,
    "FOUR": 4,
    "FIVE": 5,
    "SIX": 6,
    "SEVEN": 7,
}
USER_AGE = {
    "AGE":38
}

MAYOPIA_SNELLEN_FRACTION = {
    "left": {
        "6/6": 0.7275,
        "6/7.5": 0.7275,
        "6/9.6": 0.91,
        "6/12": 1.164,
        "6/13.5": 1.455,
        "6/15": 1.64,
        "6/16.5": 2.01,
        "6/17.7": 2.01,
        "6/19.5": 2.15,
        "6/21.45": 2.365,
        "6/24": 2.6,
        "6/25.56": 2.91,
        "6/27": 3.1,
        "6/30": 3.63,
        "6/37.5": 3.63,
        "6/48": 4.54,
        "6/60": 5.82,
        "6/90": 7.27,
        "6/120": 10.9125
    },
    "right": {
        "6/6":0.91,
        "6/7.5":1.164,
        "6/9.6":1.455,
        "6/12":1.64,
        "6/13.5":1.82,
        "6/15":2.01,
        "6/16.5":2.15,
        "6/17.7":2.365,
        "6/19.5":2.6,
        "6/21.45":2.91,
        "6/24":3.1,
        "6/25.56":3.27,
        "6/27":3.63,
        "6/30":4.54,
        "6/37.5":5.82,
        "6/48":7.27,
        "6/60":10.91,
        "6/90":14.55,
        "6/120":14.55
    }
}

HYPEROPIA_SNELLEN_FRACTION = {
    "left": {
        "6/6" : 0.364,
        "6/7.5" : 0.364,
        "6/9.6" : 0.455,
        "6/12" : 0.582,
        "6/15" : 0.72,
        "6/18.9" : 0.91,
        "6/24" : 1.14,
        "6/30" : 1.45,
        "6/37.5" : 1.82,
        "6/48" : 2.27,
        "6/60" : 2.91,
        "6/90" : 3.64,
        "6/120" : 5.46,
        "6/200" : 7.27
    },
    "right": {
        "6/6" : 0.455,
        "6/7.5" : 0.582,
        "6/9.6" : 0.72,
        "6/12" : 0.91,
        "6/15" : 1.14,
        "6/18.9" : 1.45,
        "6/24" : 1.82,
        "6/30" : 2.27,
        "6/37.5" : 2.91,
        "6/48" : 3.64,
        "6/60" : 5.46,
        "6/90" : 7.27,
        "6/120" : 12.125,
        "6/200" : 12.125
    }
}

MYOPIA_ONE = ["6/120"]
MYOPIA_THREE = ["6/16.5", "6/17.7","6/19.5", "6/21.45", "6/24", "6/25.56", "6/27", "6/30", "6/37.5", "6/48","6/60", "6/90"]
MYOPIA_FOUR = ["6/12", "6/13.5", "6/15"]
MYOPIA_FIVE = ["6/6", "6/7.5", "6/9.6"]

HYPEROPIA_ONE = ["6/200"]
HYPEROPIA_THREE = ["6/18.9", "6/24", "6/30", "6/37.5", "6/48", "6/60", "6/90", "6/120"]
HYPEROPIA_FOUR = ["6/7.5", "6/12", "6/15"]
HYPEROPIA_FIVE = ["6/6", "6/9.6"]


DEGREE = {
    "A": [0,10,20,30,40],
    "B": [50,60,70,80,90],
    "C": [100,110,120,130],
    "D": [140,150,160,170,180],
}
SNELLEN_FRACTION_FOR_TEST = (
    ('myopia', 'myopia'),
    ('hyperopia', 'hyperopia'),
)
 
POWER_MAPPING = (
    ('age_power', 'AgePowerMapping'),
    ('cyl_power', 'CylPowerMapping'),
)



MYOPIA_SNELLEN_DATA = {
        "6/6": 0,
        "6/7.5": 0.25,
        "6/9.6": 0.6,
        "6/12": 1,
        "6/13.5": 1.25,
        "6/15": 1.5,
        "6/16.5": 1.75,
        "6/17.7": 2.0,
        "6/19.5": 2.25,
        "6/21.45": 2.57,
        "6/24": 3,
        "6/25.56": 3.26,
        "6/27": 3.5,
        "6/30": 4,
        "6/37.5": 5.24,
        "6/48": 7,
        "6/60": 9,
        "6/90": 14,
        "6/120": 19,
    }
HYPEROPIA_SNELLEN_DATA = {
    "6/6": 0,
    "6/7.5": 1,
    "6/9.6": 1.49,
    "6/12": 1.97,
    "6/15": 2.4,
    "6/18.9": 2.72,
    "6/24": 2.99,
    "6/30": 3.23,
    "6/37.5": 3.358,
    "6/48": 3.5,
    "6/60": 3.6,
    "6/90": 3.734,
    "6/120": 3.80,
    "6/200": 3.87,
}
AGE_POWER_MAPPING = {
    (39, 41): 1.00,
    (40, 46): 1.25,
    (45, 51): 1.50,
    (50, 56): 1.75,
    (55, 61): 2.00,
    (60, 66): 2.25,
    (65, 120): 2.50,
}

CYL_POWER_MAPPING = {
    (-1, 5): 0.25,
    (4, 8): 0.5,
    (7, 11): 0.75,
    (10, 14): 1,
    (13, 17): 1.25,
    (16, 19): 1.5,
    (18, 21): 1.75,
    (19, 22): 2.0,
    (20, 23): 2.25,
    (21, 24): 2.5,
    (22, 25): 2.75,
    (23, 26): 3.0,
    (24, 27): 3.5,
    (26, 28): 4.0,
    (27, 29): 4.5,
    (28, 30): 5.0,
}


# WORDS = [
#     "Vision",
#     "Optometry",
#     "Eyelashes",
#     "Retina",
#     "Ophthalmology",
#     "Pupil",
#     "Contact lenses",
#     "Optometrist",
#     "Cornea",
#     "Visual acuity",
#     "Eyestrain",
#     "Eye chart",
#     "Eyelid",
#     "Astigmatism",
#     "Refraction",
#     "Eye examination",
#     "Glaucoma",
#     "Eye drops",
#     "Cataract",
#     "Binocular vision",
#     "Myopia",
#     "Presbyopia",
#     "Visual field",
#     "Color blindness",
#     "Fundus",
#     "Diopter",
#     "Perimetry",
#     "Snellen chart",
#     "Near vision",
#     "Farsightedness",
#     "Eye pressure",
#     "Pachymetry",
#     "Visual perception",
#     "Ophthalmoscope",
#     "Strabismus",
#     "Optic nerve",
#     "Tonometry",
#     "Retinoscope",
#     "Ocular health",
#     "Vision therapy"
# ]


WORDS = [
    "Marvel",
    "Basket",
    "Laptop",
    "Juggle",
    "Sphere",
    "Whisper",
    "Puddle",
    "Safari",
    "Rocket",
    "Bakery"
]


SINGLE_TEXT=[
    "C",
    "G",
    "H",
    "M",
    "K",
    "J",
    "D",
    "W",
    "Q",
    "L",
    "Y"
]


LANGUAGE_PREFERENCES = ((1,"HINDI"),(2,"ENGLISH"),(3,"PUNJABI"),(4,"KANNADA"),(5,"TAMIL"),(6,"TELUGU"))

HINDI = 1
ENGLISH = 2
PUNJABI = 3
KANNADA = 4
TAMIL = 5
TELUGU = 6


SUNGLASS_OPTIONS =  ((1,"Squared"),(2," Round"),(3,"Triangle"),(4,"Rectangular"),(5,"Oblong"))
SQUARED = 1
ROUND = 2
TRIANGLE = 3
RECTANGULAR = 4
OBLONG = 5


SHAPE_CHOICES = [
        ('oval', 'Oval'),
        ('squared', 'Squared'),
        ('round', 'Round'),
        ('triangle', 'Triangle'),
        ('rectangular', 'Rectangular'),
        ('oblong', 'Oblong'),
]
