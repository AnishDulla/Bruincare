from flask import Flask, request, render_template
import openai

openai.api_key = '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'

name = 'Bruincare'
role = 'a dedicated assistant aimed to help User with their mental health crisis and needs. do not recommend going to therapy / seeing counselor as that is what the patient is doing next anyways.'

impersonated_role = "From now on you are going to act as {}".format(role)

app = Flask(__name__)

def chatcompletion(user_input, impersonated_role, chat_history):
  output = openai.chat.completions.create(
    model="gpt-3.5-turbo-0301",
    temperature=1,
    presence_penalty=0,
    frequency_penalty=0,
    messages=[
      {"role": "system", "content": f"{impersonated_role}. Conversation history: {chat_history}"},
      {"role": "user", "content": user_input}
    ]
  )

  chatgpt_output = output.choices[0].message.content
  return chatgpt_output


def chatsummarize(user_input, impersonated_role, first_name):
  output = openai.chat.completions.create(
    model="gpt-3.5-turbo-0301",
    temperature=1,
    presence_penalty=0,
    frequency_penalty=0,
    messages=[
      {"role": "system", "content": f"{impersonated_role}"},
      {"role": "user", "content": f"Summarize this conversation with {first_name} in 500 words or less: {user_input}."}

    ]
  )

  chatgpt_output = output.choices[0].message.content
  return chatgpt_output


def severityscore(user_input, impersonated_role):
  output = openai.chat.completions.create(
    model="gpt-3.5-turbo-0301",
    temperature=1,
    presence_penalty=0,
    frequency_penalty=0,
    messages=[
      {"role": "system", "content": f"{impersonated_role}"},
      {"role": "user", "content": f"Return an integer severity score from 1 - 4 based on how severe this mental health crisis is: {user_input}. For example, if general anxiety, return 1. If sucidial thoughts or evident self harm, return 4."}

    ]
  )

  chatgpt_output = output.choices[0].message.content
  return chatgpt_output

def get_first_name(full_name):
  return full_name.split()[0] if full_name.strip() else full_name

@app.route('/', methods=['GET', 'POST'])
def home():
  if request.method == 'POST':
    full_name = request.form.get('full_name')
    first_name = get_first_name(full_name)
    bruin_id = request.form.get('bruin_id')
    email = request.form.get('email')
    insurance_plan = request.form.get('insurance_plan')

    text_input = request.form.get('text_input')
    chat_history = request.form.get('history')

    chatgpt_output = chatcompletion(text_input, impersonated_role, chat_history).replace(f'{role}:', '')
    chat_history += f'<div class="user-message"> {first_name}: {text_input}</div>'
    chat_history += f'<div class="bruincare-message"> {name}: {chatgpt_output}</div>'
    chat_history_html_formatted = chat_history.replace('\n', '<br>')

    return render_template('submit_form.html', chat_history_html_formatted=chat_history_html_formatted,
                           chat_history=chat_history, full_name=full_name, bruin_id = bruin_id, email = email, insurance_plan = insurance_plan)

  return render_template('home_page.html')

@app.route('/finish', methods=['POST'])
def finish():
    full_name = request.form.get('full_name')
    first_name = get_first_name(full_name)
    email = request.form.get('email')
    bruin_id = request.form.get('bruin_id')
    insurance_plan = request.form.get('insurance_plan')
    chat_history = request.form.get('history')
    summarized_history = chatsummarize(chat_history, impersonated_role, first_name)
    severity_score = severityscore(summarized_history, impersonated_role)
    # You can process or format chat_history as needed
    return render_template('finish_page.html', chat_history=chat_history, full_name = full_name, email = email, bruin_id = bruin_id, insurance_plan = insurance_plan, summarized_history = summarized_history, severity_score = severity_score)

if __name__ == '__main__':
    app.run(debug=True, port = 5029)
