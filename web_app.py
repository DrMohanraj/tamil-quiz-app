import os
from flask import Flask, render_template
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # 1. கோப்பு இருக்கும் சரியான பாதையைக் கண்டறிதல்
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'tamil_quiz_data.csv')
        
        # 2. UTF-8 Encoding உடன் வாசித்தல் (தமிழ் எழுத்துக்களுக்கு கட்டாயம் தேவை)
        df = pd.read_csv(csv_path, encoding='utf-8')
        
        # காலி இடங்களை (NaN) சரிசெய்தல்
        df = df.fillna("")
        
        # Dataframe-ஐ Dictionary-ஆக மாற்றுதல்
        quiz_data = df.to_dict(orient='records')
        
        # Javascript-க்கு அனுப்ப JSON-ஆக மாற்றுதல்
        quiz_json = json.dumps(quiz_data, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        quiz_json = "[]"

    # HTML-க்கு தரவுகளை அனுப்புதல்
    return render_template('index.html', backend_data=quiz_json)

if __name__ == '__main__':
    # 3. Render வழங்கும் Port-ஐப் பயன்படுத்துதல்
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
