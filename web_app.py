import os
from flask import Flask, render_template
import csv
import json

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # கோப்பு இருக்கும் சரியான பாதையைக் கண்டறிதல்
        base_dir = os.path.dirname(os.path.abspath(__file__))
        csv_path = os.path.join(base_dir, 'tamil_quiz_data.csv')
        
        quiz_data = []
        
        # Python-இன் in-built CSV மாட்யூலைப் பயன்படுத்தி வாசித்தல்
        with open(csv_path, mode='r', encoding='utf-8') as file:
            csv_reader = csv.DictReader(file)
            for row in csv_reader:
                # காலி இடங்களை (NaN) சரிசெய்தல்
                clean_row = {k: (v if v is not None else "") for k, v in row.items()}
                quiz_data.append(clean_row)
        
        # Javascript-க்கு அனுப்ப JSON-ஆக மாற்றுதல்
        quiz_json = json.dumps(quiz_data, ensure_ascii=False)
        
    except Exception as e:
        print(f"Error reading CSV: {e}")
        quiz_json = "[]"

    # HTML-க்கு தரவுகளை அனுப்புதல்
    return render_template('index.html', backend_data=quiz_json)

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
