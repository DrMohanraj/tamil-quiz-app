import os
import sys
import subprocess
import csv
import random

# 1. Open-tamil பேக்கேஜ் இருக்கிறதா எனச் சரிபார்த்து, இல்லை என்றால் தானாக இன்ஸ்டால் செய்யும் மேஜிக் கோட்
try:
    from tamil import utf8
except ImportError:
    print("Open-Tamil பேக்கேஜ் இன்ஸ்டால் ஆகவில்லை. இப்போது தானாக இன்ஸ்டால் ஆகிறது. தயவுசெய்து காத்திருக்கவும்...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "open-tamil"])
    print("இன்ஸ்டால் முடிந்தது! நிரல் தொடர்கிறது...\n")
    from tamil import utf8

# 2. உங்கள் CSV கோப்பின் பெயர் (எக்செல் பைல்)
csv_file = "tamil_quiz_data.csv"

# பைல் இருக்கிறதா என செக் செய்தல்
if not os.path.exists(csv_file):
    print(f"பிழை: '{csv_file}' என்ற பைல் இந்த ஃபோல்டரில் இல்லை.")
    print("பைத்தானையும் CSV பைலையும் ஒரே ஃபோல்டரில் (Folder) வைக்கவும்.")
else:
    # 3. CSV பைலைப் படித்துக் கேள்வியைத் தேர்ந்தெடுத்தல்
    with open(csv_file, mode='r', encoding='utf-8') as file:
        csv_reader = csv.DictReader(file)
        data_list = list(csv_reader)
        
        if len(data_list) == 0:
            print("CSV பைலில் எந்தத் தரவும் இல்லை.")
        else:
            random_row = random.choice(data_list)
            
            கேள்வி = random_row.get('கேள்வி', '')
            முழு_விடை = random_row.get('முழுமையான வாக்கியம் (விடை)', '')
            கலைக்க_வேண்டியவை = str(random_row.get('கலைக்கப்பட வேண்டிய சொற்கள்', ''))
            
            print("--------------------------------------------------")
            print(f"கேள்வி: {கேள்வி}")
            print(f"விடை: {முழு_விடை}")
            print("--------------------------------------------------")
            
            # 4. சொற்களைப் பிரித்துக் கலைத்தல்
            சொற்கள்_பட்டியல் = கலைக்க_வேண்டியவை.split(',')
            
            for சொல் in சொற்கள்_பட்டியல்:
                சுத்தமான_சொல் = சொல்.strip()
                if சுத்தமான_சொல்:
                    எழுத்துகள் = utf8.get_letters(சுத்தமான_சொல்)
                    கலைத்த_எழுத்துகள் = எழுத்துகள்.copy()
                    
                    # எழுத்துகள் கலைக்கப்படுவதை உறுதி செய்தல்
                    while கலைத்த_எழுத்துகள் == எழுத்துகள் and len(எழுத்துகள்) > 1:
                        random.shuffle(கலைத்த_எழுத்துகள்)
                        
                    print(f"உண்மையான சொல்: {சுத்தமான_சொல்}")
                    print(f"விளையாட்டிற்கான கலைக்கப்பட்ட எழுத்துகள்: {கலைத்த_எழுத்துகள்}")
                    print("---")
