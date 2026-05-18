from flask import Flask, render_template
import pandas as pd
import json

app = Flask(__name__)

@app.route('/')
def home():
    try:
        # CSV ஃபைலை வாசித்தல்
        df = pd.read_csv('tamil_quiz_data.csv')
        
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
    app.run(debug=True, host='0.0.0.0', port=5000)
