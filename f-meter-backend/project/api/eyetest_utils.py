from google.api_core.client_options import ClientOptions
from google.cloud.speech_v2.types import cloud_speech
from google.cloud import speech_v1p1beta1 as speech
from google.cloud.speech_v2 import SpeechClient
from google.cloud import texttospeech
from .serializer import *
from .constants import *
from .models import *
import pandas as pd
import random
import os
from decouple import config
GOOGLE_CREDENTIALS = config('GOOGLE_CREDENTIALS')
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = GOOGLE_CREDENTIALS

"""
Get test object function
"""
def get_test_obj(test_id):
    try:
        return EyeTest.objects.get(pk=test_id)
    except (EyeTest.DoesNotExist):
        return None

"""
create serializer function
"""
def create_test_serializer(text_obj, data):
    return EyeTestSerializer(instance=text_obj, data=data)

"""
Get user object function
"""
def get_user(user_id):
    try:
        return User.objects.get(id=user_id)
    except User.DoesNotExist:
        return None
    
"""
automaticaly seleted test based on qestion, function
"""
# def selete_test_behalf_of_question(user, selected_question):
#     if int(user.age) < USER_AGE["AGE"]:
#         if selected_question == [QUESTION_CONSTANT["ONE"], QUESTION_CONSTANT["TWO"]] or selected_question == [QUESTION_CONSTANT["ONE"]] or selected_question == [ QUESTION_CONSTANT["TWO"]]:
#             test = VISION_TEST_CHOICES[0][0]
#         elif selected_question == [QUESTION_CONSTANT["THREE"], QUESTION_CONSTANT["FIVE"]] or selected_question == [QUESTION_CONSTANT["THREE"]] or selected_question == [QUESTION_CONSTANT["FIVE"]]:
#             test = VISION_TEST_CHOICES[1][0]
#         elif selected_question == [QUESTION_CONSTANT["ONE"], QUESTION_CONSTANT["TWO"], QUESTION_CONSTANT["THREE"], QUESTION_CONSTANT["FOUR"], QUESTION_CONSTANT["FIVE"]]:
#             test = VISION_TEST_CHOICES[2][0]
#         else:
#             return None
#     else:
#         test = VISION_TEST_CHOICES[2][0]    
#     return test


"""
automaticaly seleted test based on qestion, function
"""
def selete_test_behalf_of_question(selected_question):
    test = None
    message = "Please read questions carefully"
    selected_question = sorted(selected_question)
    if 2 in selected_question and 1 not in selected_question:
        message = message
    elif  (3 in selected_question and 4 in selected_question):
        message = message
    elif (selected_question == [3]) or (selected_question == [1,2,3] or selected_question == [1,3]):
        test = "myopia"
    elif selected_question == [4] or (selected_question == [1,2,4] or selected_question == [1,4]):
        test = "hyperopia"
    return test , message  
    
    
    
"""
    Get the text size based on vision test, action, and snellen fraction.
"""
def get_text_size(vision_test, action, snellen_fraction, text_obj):
   
    myopia_text_size = SnellenFraction.objects.filter(test="myopia", snellen_fraction=snellen_fraction).first()
    hyperopia_text_size = SnellenFraction.objects.filter(test="hyperopia", snellen_fraction=snellen_fraction).first()
   
    if text_obj.test == VISION_TEST_CHOICES[0][0] or (text_obj.test == VISION_TEST_CHOICES[2][0] and vision_test == VISION_TEST_CHOICES[0][0]):
        text_size = myopia_text_size.left_action if action == "left" else myopia_text_size.right_action
    elif text_obj.test == VISION_TEST_CHOICES[1][0] or (text_obj.test == VISION_TEST_CHOICES[2][0] and vision_test == VISION_TEST_CHOICES[1][0]):
        text_size = hyperopia_text_size.left_action if action == "left" else hyperopia_text_size.right_action
    else:
        text_size = None
   
    return text_size
 
empty_list = []
 
"""
Get Random text, function
"""
def get_random_text(vision_test, text_obj, snellen_fraction):
    global empty_list
    if text_obj.test == VISION_TEST_CHOICES[0][0] or (text_obj.test == VISION_TEST_CHOICES[2][0] and vision_test ==VISION_TEST_CHOICES[0][0]):
           
        if snellen_fraction in MYOPIA_ONE:
            letter = "one"
        elif snellen_fraction in MYOPIA_THREE:
            letter = "three"
        elif snellen_fraction in MYOPIA_FOUR:
            letter = "four"
        elif snellen_fraction in MYOPIA_FIVE:
            letter = "five"
 
    elif text_obj.test == VISION_TEST_CHOICES[1][0] or (text_obj.test == VISION_TEST_CHOICES[2][0] and vision_test ==VISION_TEST_CHOICES[1][0]):
 
        if snellen_fraction in HYPEROPIA_ONE:
            letter = "one"
        if snellen_fraction in HYPEROPIA_THREE:
            letter = "three"
        elif snellen_fraction in HYPEROPIA_FOUR:
            letter = "four"
        elif snellen_fraction in HYPEROPIA_FIVE:
            letter = "five"
 
    all_items = NumberOfLetterInText.objects.all()
    if not all_items:
        return None
   
    unused_items = all_items.filter(used=False, number_of_letter = letter)
    if unused_items:
        random_item = random.choice(unused_items)
        random_item.used = True
        random_item.save()
    else:
        NumberOfLetterInText.objects.filter(number_of_letter = letter).update(used=False)
        random_item = random.choice(all_items.filter(used=False, number_of_letter = letter))
 
    if random_item.text in empty_list:
        random_item.used = True
        random_item.save()
        NumberOfLetterInText.objects.filter(number_of_letter = letter).update(used=False)
        random_item = random.choice(all_items.filter(used=False, number_of_letter = letter))
    empty_list.clear()    
    empty_list.append(random_item.text)
    return random_item

"""
Set Snellen fraction Based On Test, function
"""
def set_snellen_fraction_based_on_test(text_obj, snellen_fraction, serializer, vision_test):
    if text_obj.test == "myopia":
            serializer.validated_data["myopia_snellen_fraction"] = snellen_fraction
    if text_obj.test == "hyperopia":
        serializer.validated_data["hyperopia_snellen_fraction"] = snellen_fraction
    if text_obj.test == "presbyopia":
        if vision_test == 'myopia':
            serializer.validated_data["myopia_snellen_fraction"] = snellen_fraction
        else:
            serializer.validated_data["hyperopia_snellen_fraction"] = snellen_fraction
    return serializer
 
 
"""
Get degree, function
"""
def get_degree(text_obj):
    if text_obj.choose_astigmatism == "a":
        GET_DEGREES = DEGREE["A"]
    elif text_obj.choose_astigmatism == "b":
        GET_DEGREES = DEGREE["B"]
    elif text_obj.choose_astigmatism == "c":
        GET_DEGREES = DEGREE["C"]
    elif text_obj.choose_astigmatism == "d":
        GET_DEGREES = DEGREE["D"]
    return  GET_DEGREES
 
"""
Get cyl power, function
"""
def get_eye_cyl_power(cyl_text_size):
    if cyl_text_size is not None:
        cyl_text_size = float(cyl_text_size)
        power_mapping = PowerMapping.objects.filter(power_mapping = "cyl_power", start_range__lt=cyl_text_size, end_range__gt=cyl_text_size).first()
        return power_mapping.power if power_mapping else 0
    return 0  
 
"""
read csv and get all columns data, function
"""
def constant_data_insert_in_db_from_csv():
    FILE_PATH = os.path.join('eye-test-data', 'eye_data_extended.xlsx')
    xlsx_file_path = FILE_PATH
    df = pd.read_excel(xlsx_file_path)
    column_data_dict = {}
    for column_name in df.columns:
        column_data = df[column_name].tolist()
        cleaned_column_data = [item for item in column_data if not pd.isna(item)]
        column_data_dict[column_name] = cleaned_column_data
    return column_data_dict
 
"""
insert data in NumberOfLetterInText table, function
"""
def crate_data_of_NumberOfLetterInText_model(data):
        data_to_create = []
        for text in data['Three Text']:
            data_to_create.append(NumberOfLetterInText(number_of_letter='three', text=text))
        for text in data['Four Text']:
            data_to_create.append(NumberOfLetterInText(number_of_letter='four', text=text))
        for text in data['Five Text']:
            data_to_create.append(NumberOfLetterInText(number_of_letter='five', text=text))
        NumberOfLetterInText.objects.bulk_create(data_to_create)
   
"""
insert data in SnellenFraction table, function
"""
def crate_data_of_SnellenFraction_model(data):
        myopia_instances = [
            SnellenFraction(test='myopia', snellen_fraction=fraction, power=power, left_action=left, right_action=right)
            for fraction, power, left, right in zip(data['Myopia Snellen Fraction'], data['Myopia Power'], data['Text Size Myopia Left'], data['Text Size Myopia Right'])
        ]
        hyperopia_instances = [
            SnellenFraction(test='hyperopia', snellen_fraction=fraction, power=power, left_action=left, right_action=right)
            for fraction, power, left, right in zip(data['Hyperopia Snellen Fraction'], data['Hyperopia Power'], data['Text Size Hyperopia Left'], data['Text Size Hyperopia Right'])
        ]
        SnellenFraction.objects.bulk_create(myopia_instances + hyperopia_instances)
 
"""
insert data in PowerMapping table, function
"""
def crate_data_of_PowerMapping_model(data):
        age_power_instances = [
            PowerMapping(power_mapping='age_power', start_range=start, end_range=end, power=power)
            for start, end, power in zip(data['Age Range Start'], data['Age Range End'], data['Age Power'])
        ]
        cyl_power_instances = [
            PowerMapping(power_mapping='cyl_power', start_range=start, end_range=end, power=power)
            for start, end, power in zip(data['Cylinder Range Start'], data['Cylinder Range End'], data['Cylinder Power'])
        ]
        PowerMapping.objects.bulk_create(age_power_instances + cyl_power_instances)




"""
Get cyl power, function
"""
def get_eye_cyl_power(test_obj):
    eye_cyl_power = 0
    if test_obj.cyl_text_size is not None:
        cyl_snellen_fraction = float(test_obj.cyl_text_size)
        for eye_cyl_range, power in CYL_POWER_MAPPING.items():
            if eye_cyl_range[0] < cyl_snellen_fraction < eye_cyl_range[1]:
                eye_cyl_power = power
                break
    return eye_cyl_power
 
 
"""
Get Age power, function
"""
def get_age_power(test_obj):
    age_power = 0
    age = int(test_obj.test_of_user.age)
    for age_range, power in AGE_POWER_MAPPING.items():
        if age_range[0] < age < age_range[1]:
            age_power = power
            break
    return age_power    
 
"""
Get Report Data For Presbiyopia Test, function
"""
def get_report_data_for_presbiyopia(test_obj):
        myopia_SPH_value = MYOPIA_SNELLEN_DATA.get(
            test_obj.myopia_snellen_fraction, 0
        )
        hyperopia_SPH_value = HYPEROPIA_SNELLEN_DATA.get(
            test_obj.hyperopia_snellen_fraction, 0
        )
 
        age_power = get_age_power(test_obj)
        eye_cyl_power = get_eye_cyl_power(test_obj)
 
        if myopia_SPH_value != 0 and test_obj.myopia_snellen_fraction:
            myopia_SPH_value = -(myopia_SPH_value - eye_cyl_power)
            # myopia_SPH_value = round(myopia_SPH_value, 2)
            if myopia_SPH_value > 0:
                myopia_SPH_value = -myopia_SPH_value
            myopia_SPH_value = round(myopia_SPH_value, 2)
 
        test_obj.myopia_sph_power = myopia_SPH_value
        test_obj.hyperopia_sph_power = hyperopia_SPH_value
        test_obj.cyl_power = -(eye_cyl_power)
        test_obj.age_power = age_power
        return test_obj
 
"""
Get Report Data For Myopia and Hyperopia Test, function
"""
def get_report_data_for_myopia_and_hyperopia(test_obj):
    if test_obj.test == "myopia":
        target_value = test_obj.myopia_snellen_fraction
        data = MYOPIA_SNELLEN_DATA
    elif test_obj.test == "hyperopia":
        target_value = test_obj.hyperopia_snellen_fraction
        data = HYPEROPIA_SNELLEN_DATA
    SPH_value = data.get(target_value, 0)
 
    eye_cyl_power = get_eye_cyl_power(test_obj)

    test_obj.sph_power = SPH_value
    if SPH_value != 0 and test_obj.test == "myopia":
        SPH_value = -(SPH_value - eye_cyl_power)
        if SPH_value > 0:
            SPH_value = -SPH_value
        SPH_value = round(SPH_value, 2)
        test_obj.myopia_sph_power = SPH_value    
 
    elif test_obj.test == "hyperopia":  
        test_obj.hyperopia_sph_power = SPH_value          
    test_obj.cyl_power = -eye_cyl_power
    return test_obj



"""
Convert Text to Speech, function
"""
def text_to_speech(text, language):
 
    if language == HINDI:
        language_code = "hi-IN"
        voice_name = "hi-IN-Wavenet-D"
    elif language == ENGLISH:
        language_code = "en-US"
        voice_name = "en-US-Standard-C"
    elif language == PUNJABI:
        language_code = "pa-IN"
        voice_name = "pa-IN-Wavenet-D"
    elif language == KANNADA:
        language_code = "kn-IN"
        voice_name = "kn-IN-Wavenet-A"
    elif language == TELUGU:
        language_code = "te-IN"
        voice_name = "te-IN-Standard-A"
    elif language == TAMIL:
        language_code = "ta-IN"
        voice_name = "ta-IN-Standard-A"
    else:
        raise ValueError("Unsupported language")
 
    client = texttospeech.TextToSpeechClient()
    input_text = texttospeech.SynthesisInput(text=text)
    voice = texttospeech.VoiceSelectionParams(
        language_code=language_code,
        name=voice_name,
        ssml_gender=texttospeech.SsmlVoiceGender.FEMALE,
    )
    audio_config = texttospeech.AudioConfig(
        audio_encoding=texttospeech.AudioEncoding.MP3
    )
    response = client.synthesize_speech(
        input=input_text, voice=voice, audio_config=audio_config
    )
    output_file_path = "output.mp3"
 
    with open(output_file_path, "wb") as audio_file:
        audio_file.write(response.audio_content)
 
    return response.audio_content



"""
Get Random Word, function
"""
last_word= []
word_copy = list(WORDS)
def get_random_word():
    global word_copy
    global WORDS
    if word_copy:
        random_word = random.choice(word_copy)  
        word_copy.remove(random_word)
        last_word.clear()
        last_word.append(random_word)
        return random_word
    else:
        word_copy = list(WORDS)
        random_word = random.choice(word_copy)  
        if last_word[0] == random_word:
            word_copy.remove(random_word)
            random_word = random.choice(word_copy)  
            last_word.clear()
            last_word.append(random_word)
            return random_word
        else:
            return random_word
 
"""
Get Randomv Word size, function
"""
def get_random_word_size(test_obj, snellen_fraction):
    hyperopia_text_size = SnellenFraction.objects.filter(test=VISION_TEST_CHOICES[1][0], snellen_fraction=snellen_fraction).first()
    text_size = hyperopia_text_size.left_action
    return 2*(text_size)


"""
    Get the text size for red and green test, function
"""
def get_text_size_for_red_and_green(snellen_fraction, text_obj):
    myopia_text_size = SnellenFraction.objects.filter(test=VISION_TEST_CHOICES[0][0], snellen_fraction=snellen_fraction).first()
    hyperopia_text_size = SnellenFraction.objects.filter(test=VISION_TEST_CHOICES[1][0], snellen_fraction=snellen_fraction).first()
    if myopia_text_size or hyperopia_text_size:
        if text_obj.test == VISION_TEST_CHOICES[0][0]:
            text_size = myopia_text_size.left_action
        elif text_obj.test == VISION_TEST_CHOICES[1][0]:
            text_size = hyperopia_text_size.left_action
        else:
            text_size = None
        return 2*(text_size)
    else:
        text_size = None
    


counter = 0
first_action = None
second_action = None
third_action = None
 
first_snellen_fraction = None
second_snellen_fraction = None
third_snellen_fraction = None

def get_snellen_fraction_according_red_and_green_action(test_obj, snellen_fraction, action):
    get_all_snellen_fraction = list(SnellenFraction.objects.filter(test=test_obj.test).values_list("snellen_fraction", flat=True))
    if snellen_fraction in get_all_snellen_fraction:
        index = get_all_snellen_fraction.index(snellen_fraction)
 
        if action == "red":
            if index > 0:
                previous_element = get_all_snellen_fraction[index - 1]
                element = previous_element
            else:
                element = get_all_snellen_fraction[0]
        else:
            if index < len(get_all_snellen_fraction) - 1:
                next_element = get_all_snellen_fraction[index + 1]
                element = next_element
            else:
                element = get_all_snellen_fraction[-1]
        return element
    else:
        return None


empty_list_for_RD_test = []

def get_random_text_for_red_and_green(test_obj, snellen_fraction):
    global empty_list_for_RD_test
    letter = None
    if test_obj.test == VISION_TEST_CHOICES[0][0]:
        if snellen_fraction in MYOPIA_ONE:
            letter = "one"
        elif snellen_fraction in MYOPIA_THREE:
            letter = "three"
        elif snellen_fraction in MYOPIA_FOUR:
            letter = "four"
        elif snellen_fraction in MYOPIA_FIVE:
            letter = "five"
 
    elif test_obj.test == VISION_TEST_CHOICES[1][0]:
        if snellen_fraction in HYPEROPIA_ONE:
            letter = "one"
        if snellen_fraction in HYPEROPIA_THREE:
            letter = "three"
        elif snellen_fraction in HYPEROPIA_FOUR:
            letter = "four"
        elif snellen_fraction in HYPEROPIA_FIVE:
            letter = "five"

    all_items = NumberOfLetterInText.objects
    unused_items = all_items.filter(used=False, number_of_letter=letter)

    if unused_items:
        random_item = random.choice(unused_items)
        random_item.used = True
        random_item.save()
    else:
        all_items.filter(number_of_letter=letter).update(used=False)
        random_item = random.choice(all_items.filter(used=False, number_of_letter=letter))

    if random_item.text in empty_list_for_RD_test:
        random_item.used = True
        random_item.save()
        all_items.filter(number_of_letter=letter).update(used=False)
        random_item = random.choice(all_items.filter(used=False, number_of_letter=letter))

    empty_list_for_RD_test.clear()
    empty_list_for_RD_test.append(random_item.text)
    return random_item.text


"""
This Code is required for future use
"""
# """
# Get Report Data For Presbiyopia Test, function
# """
# def get_report_data_for_presbiyopia(test_obj):

#     myopia_SPH_value = SnellenFraction.objects.filter(test="myopia",snellen_fraction=test_obj.myopia_snellen_fraction).first()
#     myopia_SPH_value = myopia_SPH_value.power if myopia_SPH_value else 0
#     hyperopia_SPH_value = SnellenFraction.objects.filter(test="hyperopia", snellen_fraction=test_obj.hyperopia_snellen_fraction).first()
#     hyperopia_SPH_value = hyperopia_SPH_value.power if hyperopia_SPH_value else 0
   
#     age = int(test_obj.test_of_user.age)
#     age_power = 0
#     age_mapping = PowerMapping.objects.filter(power_mapping = "age_power", start_range__lt=age, end_range__gt=age).first()
#     age_power = age_mapping.power if age_mapping else 0  
 
#     eye_cyl_power = get_eye_cyl_power(test_obj.cyl_text_size)
 
#     if myopia_SPH_value != 0 and test_obj.myopia_snellen_fraction:
#         myopia_SPH_value = -(myopia_SPH_value - eye_cyl_power)
#         myopia_SPH_value = round(myopia_SPH_value, 2)
#         if myopia_SPH_value > 0:
#             myopia_SPH_value = -myopia_SPH_value
#             myopia_SPH_value = round(myopia_SPH_value, 2)
 
#     test_obj.myopia_sph_power = myopia_SPH_value
#     test_obj.hyperopia_sph_power = hyperopia_SPH_value
#     test_obj.cyl_power = -(eye_cyl_power)
#     test_obj.age_power = age_power
#     return test_obj
 
# """
# Get Report Data For Myopia and Hyperopia Test, function
# """
# def get_report_data_for_myopia_and_hyperopia(test_obj):
#     if test_obj.test == VISION_TEST_CHOICES[0][0]:
#         target_value = test_obj.myopia_snellen_fraction
#         data = SnellenFraction.objects.filter(test="myopia",snellen_fraction=target_value).first()
#     elif test_obj.test == VISION_TEST_CHOICES[1][0]:
#         target_value = test_obj.hyperopia_snellen_fraction
#         data = SnellenFraction.objects.filter(test="hyperopia",snellen_fraction=target_value).first()
#     SPH_value = data.power if data else 0
 
#     eye_cyl_power = get_eye_cyl_power(test_obj.cyl_text_size)
 
#     if SPH_value != 0 and test_obj.test == VISION_TEST_CHOICES[0][0]:
#         SPH_value = -(SPH_value - eye_cyl_power)
#         if SPH_value > 0:
#             SPH_value = -SPH_value
#             SPH_value = round(SPH_value, 2)

#     print(-eye_cyl_power)        
 
#     test_obj.cyl_power = -eye_cyl_power
#     if test_obj.test == VISION_TEST_CHOICES[0][0]:        
#         test_obj.myopia_sph_power = SPH_value
#         print(SPH_value,"---------------------------------Myhopia SPH_value-------------->>>>>")        
#     if test_obj.test == VISION_TEST_CHOICES[1][0]:
#         test_obj.hyperopia_sph_power = SPH_value
#         print(SPH_value,"---------------------------------hyperopia SPH_value-------------->>>>>")         

#     return test_obj



