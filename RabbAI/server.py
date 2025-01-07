from flask import Flask, render_template, request, jsonify
import openai
from datetime import datetime

app = Flask(__name__, static_folder='static')

openai.api_key = 'secret'  

# Store user-specific preferences and saved content
user_preferences = {}
saved_dvar_torahs = {}

# Hardcoded format for Dvar Torah
FORMAT_INFO = """
The format of a Dvar Torah is as follows:
The whole dvar torah should be about 7 full paragraphs and should have the langugae level of a 14 year old. 
Here is the process of how to craft one.
1. A 3-sentence summary of the Parsha.
2. Main part: Focus on a specific message from the Parsha, including a hebrew quote. 
(DONT FORGET: when quoting from the bible, any time , you must give the quote in HEBREW text! Not transliterated) This includes quotes from various relevant biblical commentaries.
Also, provide a fleshed out sythesis of ideas, not just one. 
3. A connection to a greater lesson, addressing the current audience. covertly, make the tone and content fittig for that audience. 
4. End with very brief action, takeaway message, or blessing to the crowd. This should be brief and not redundant. 
Other guidlines: 
1. Do not number these parts, or explicitly point them out.
2. Please make the tone relaxed, without superfluod and facny wording. Speak as if you are 13 years old!!! NEver use the word divine or divine providence.
3. use the word Pasuk rather than Verse & use the word Perek rather than Chapter. Refer to pesukim and perakim by hebrew their letters ex: א rather than verse 1. 
4. dont say in the "tale of" 
5. Use the word Mefarshim or Rishonim rather than sages 
6.


"""

def build_style_instructions(style_choice, names_choice):
    style_instructions = {
        "textual": """ 
        Include insights from classical commentators like ( but not limited to!):
        Rambam, Rashi, and the Nitziv, Chizkuni, Radak, Ibn Ezra, Abarbanel, Malbim. 
        Use these names ehen referring to them.
        Choose commentaries that tie together well, rather than just bringing a random few
                      Do not explain who they are, assume we know. Do not describe them with adjectives like "esteemed" etc."
        """,
        "abstract": "Focus on broader themes without specific textual references.",
    }.get(style_choice, "No style preference provided.")
    
    naming_instructions = {
        "hebrew": "Use Hebrew names for people and places.",
        "english": "Use English names for people and places.",
    }.get(names_choice, "No naming preference provided.")
    
    return f"{style_instructions} Also in terms of names: {naming_instructions}."

import requests
from datetime import datetime

def get_current_parsha(date_str=None):
    """
    Gets the weekly Torah portion (parsha) read on the Sabbath for the specified date.
    
    Parameters:
        date_str (str, optional): Date in "YYYY-MM-DD" format. Defaults to today if not provided.
    
    Returns:
        str: The name of the weekly parsha. 
    """
    # Use today's date if no date_str is provided
    if date_str is None:
        date_str = datetime.now().strftime("%Y-%m-%d")
    
    # Parse year, month, and day for the API request
    year, month, day = date_str.split('-')
    
    # Format the URL to query the Hebcal API with dynamic date
    url = f"https://www.hebcal.com/shabbat?cfg=json&geonameid=5128581&m=50&gy={year}&gm={month}&gd={day}"
    
    # Make a request to Hebcal API
    response = requests.get(url)
    
    # Check for successful response
    if response.status_code == 200:
        data = response.json()
        for item in data['items']:
            if item['category'] == 'parashat':
                return item['title']
    
    return "Parsha not found"

# Example usage:
parsha = get_current_parsha()  # Uses today's date by default
print("This week's parsha is:", parsha)

# Or specify a date explicitly

def get_gpt_response(user_input, audience_info="", parsha_info="", styles=""):
    messages = [
        {"role": "system", "content": "You are an expert in Torah and Jewish learning, helping someone craft a perfect Dvar Torah."},
        {"role": "system", "content": FORMAT_INFO},
        {"role": "system", "content": parsha_info},
        {"role": "system", "content": audience_info},
        {"role": "system", "content": styles},
        {"role": "user", "content": user_input}
    ]
    print("Messages passed to GPT:", messages)
    response = openai.ChatCompletion.create(model="gpt-4", messages=messages, max_tokens=1500)
    return response['choices'][0]['message']['content'].strip()

@app.route('/')
def home():
    return render_template("home.html")

@app.route('/get_current_parsha', methods=['GET'])
def current_parsha():
    parsha_name = get_current_parsha()
    return jsonify({"parsha": parsha_name})

@app.route('/generate_options', methods=['POST'])
def generate_options():
    data = request.json
    user_id = data.get('user_id', 'default')

    # Update or initialize preferences for the user
    user_preferences[user_id] = {
        "parsha_info": f"This week's parsha is Parshat {data['parsha_name']}.",
        "audience_info": data['audience_info'],
        "style_choice": data.get('style_choice', ''),
        "names_choice": data.get('names_choice', '')
    }

    # Generate style instructions
    styles = build_style_instructions(
        user_preferences[user_id]["style_choice"],
        user_preferences[user_id]["names_choice"]
    )

    gpt_prompt = f"""
    Provide {data['num_options']} unique Dvar Torah topics for Parshat {data['parsha_name']}.
    Title: <Title of Option>
    Description: <Description of Option>
    Ensure each topic has a unique, descriptive title.
    """

    options_text = get_gpt_response(
        gpt_prompt,
        audience_info=user_preferences[user_id]["audience_info"],
        parsha_info=user_preferences[user_id]["parsha_info"],
        styles=styles
    )

    parsed_options = []
    current_option = {"title": "", "description": ""}
    for line in options_text.split("\n"):
        line = line.strip()
        if line.startswith("Title:"):
            current_option["title"] = line.replace("Title:", "").strip()
        elif line.startswith("Description:"):
            current_option["description"] = line.replace("Description:", "").strip()
            parsed_options.append(current_option)
            current_option = {"title": "", "description": ""}
    
    return jsonify({"options": parsed_options[:data['num_options']]})

@app.route('/dvar_torah')
def dvar_torah():
    content = request.args.get("content", "")
    return render_template("dvar_torah.html", dvar_torah=content)

@app.route('/generate_dvar_torah', methods=['POST'])
def generate_dvar_torah():
    data = request.json
    user_id = data.get('user_id', 'default')

    selected_option = "topic to write about " + data['selected_option']
    user_prefs = user_preferences.get(user_id, {})

    if not user_prefs:
        return jsonify({"error": "User preferences not set"}), 400

    styles = build_style_instructions(
        user_prefs.get("style_choice", ''),
        user_prefs.get("names_choice", '')
    )

    dvar_torah = get_gpt_response(
        selected_option,
        audience_info=user_prefs.get("audience_info", "No audience information provided."),
        parsha_info=user_prefs.get("parsha_info", "No Parsha information provided."),
        styles=styles
    )

    dvar_torah_formatted = "".join(f"<p>{para.strip()}</p>" for para in dvar_torah.split('\n') if para.strip())

    # Save current draft and update previous draft for the user
    if user_id not in saved_dvar_torahs:
        saved_dvar_torahs[user_id] = {"current": dvar_torah_formatted, "previous": None}
    else:
        saved_dvar_torahs[user_id]["previous"] = saved_dvar_torahs[user_id]["current"]
        saved_dvar_torahs[user_id]["current"] = dvar_torah_formatted

    return jsonify({"dvar_torah": dvar_torah_formatted})

@app.route('/refine_dvar_torah', methods=['POST'])
def refine_dvar_torah():
    data = request.json
    user_id = data.get('user_id', 'default')
    current_content = data.get("content", "")
    refinement = data.get("refinement", "")

    user_prefs = user_preferences.get(user_id, {})
    if not user_prefs:
        return jsonify({"error": "User preferences not set"}), 400

    audience_info = user_prefs.get("audience_info", "No audience information provided.")
    parsha_info = user_prefs.get("parsha_info", "No Parsha information provided.")
    style_choice = user_prefs.get("style_choice", "No style preference provided.")
    names_choice = user_prefs.get("names_choice", "No naming preference provided.")
    styles = build_style_instructions(style_choice, names_choice)

    refined_prompt = (
        f"Refine the following Dvar Torah while keeping the original style and preferences. BUT, make sure to now:  "
        f"{refinement}\n\nOriginal Dvar Torah:\n{current_content}"
    )

    refined_content = get_gpt_response(
        refined_prompt,
        audience_info=audience_info,
        parsha_info=parsha_info,
        styles=styles
    )

    refined_content_formatted = "".join(
        f"<p>{para.strip()}</p>" for para in refined_content.split('\n') if para.strip()
    )

    # Update previous and current drafts
    if user_id not in saved_dvar_torahs:
        saved_dvar_torahs[user_id] = {"current": refined_content_formatted, "previous": None}
    else:
        saved_dvar_torahs[user_id]["previous"] = saved_dvar_torahs[user_id]["current"]
        saved_dvar_torahs[user_id]["current"] = refined_content_formatted

    return jsonify({"refined_dvar_torah": refined_content_formatted})

@app.route('/save_manual_edit', methods=['POST'])
def save_manual_edit():
    data = request.json
    user_id = data.get('user_id', 'default')
    updated_content = data.get('content', '')

    if user_id in saved_dvar_torahs:
        # Update the current draft with the manually edited content
        saved_dvar_torahs[user_id]["previous"] = saved_dvar_torahs[user_id]["current"]
        saved_dvar_torahs[user_id]["current"] = updated_content
        return jsonify({"success": True})
    else:
        return jsonify({"error": "User drafts not found"}), 404

@app.route('/restore_previous_draft', methods=['POST'])
def restore_previous_draft():
    data = request.json
    user_id = data.get("user_id", "default")
    
    if user_id in saved_dvar_torahs and saved_dvar_torahs[user_id]["previous"]:
        # Swap current and previous drafts
        saved_dvar_torahs[user_id]["current"], saved_dvar_torahs[user_id]["previous"] = (
            saved_dvar_torahs[user_id]["previous"],
            saved_dvar_torahs[user_id]["current"]
        )
        return jsonify({"restored_dvar_torah": saved_dvar_torahs[user_id]["current"]})
    else:
        return jsonify({"error": "No previous draft to restore"}), 404
    
if __name__ == '__main__':
    app.run(debug=True)
