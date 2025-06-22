from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import auth
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
#from .models import UserProfile

from openai import OpenAI

import base64
import json
import os

def go_to_target(request):
    return render(request, 'contract.html')

openai_api_key = ""

client = OpenAI(api_key = openai_api_key)

def load_db(filename):
    with open(filename, "r", encoding="utf-8") as f:
        return json.load(f)

def save_db(data, filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

@csrf_exempt
def submit_signature(request):
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        signature_data = data.get('signature')

        if signature_data and signature_data.startswith("data:image/png;base64,"):
            encoded = signature_data.split(',')[1]
            decoded_data = base64.b64decode(encoded)

            path = 'media/signatures'
            os.makedirs(path, exist_ok=True)

            with open(os.path.join(path, 'signature.png'), 'wb') as f:
                f.write(decoded_data)

            return JsonResponse({'status': 'success'})

    return JsonResponse({'status': 'error'})


def ask_ai_to_manage(json_data1, json_data2, user_command):
    system_prompt = """
You are a JSON retrieval assistant.

You will receive two JSON arrays and a user command.
Your job is to extract exactly one matching entry from the JSON arrays based on the command and user information.

⚠️ Always return a single JSON object only (not an array).
⚠️ Do NOT explain or comment.
⚠️ Your response must be a valid JSON object only.
⚠️ No markdown, no text, no code block — just the pure JSON object.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": f"JSON Data:\n{json.dumps(json_data1, indent=2)}"},
        {"role": "user", "content": f"User information:\n{json.dumps(json_data2, indent=2)}"},
        {"role": "user", "content": f"Command:\n{user_command}"}
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages
    )

    return json.loads(response.choices[0].message.content)


message_contract = '''
View the AI generation contract
The Automated E-Contract Generator is a system that uses AI to automatically generate customized electronic contracts based on the selected lesson type (single sessions, long-term programs, group classes). The system streamlines the contracting process, reduces misunderstandings, and builds trust between users.
→ If you select a teacher and choose a class type, an online contract will come out accordingly. The contents of the online contract are as follows.
Both parties
Lesson details (type, session, dates, time, location)
Fees and payments (Total fee, payment method, refund)
Cancellation policy
Instructor’s Obligations
Student’s Obligations
Privacy
Dispute Resolution
→ If the parties tell you what they want to add or modify, it will be immediately reflected.
→ These contracts are confirmed and signed by both parties to have legal effect.
→ Example of a teacher's contract clause (It needs to be revised because it is not a mutual contract.) 
	→ Introduction of electronic signatures

AI-Powered Contract Clause Warnings
Before users write and sign contracts online, AI automatically analyzes them to check one by one for provisions that may be problematic or unfavorable to users, ask the user to check and confirm for each clause.
→ When the contract is drafted, the AI automatically scans the entire content and automatically detects risk/disadvantage clauses.
→ Prepare a checklist of detected risk clauses. Examples of risk clauses are as follows.
Strict cancellation policy
Automatic renewal
Hidden fees
Unilateral modification rights
→ For each risk clause, AI provides a summary of the provisions, an explanation of the risks, and a suggestion of recommended modification strategies.
→ Users can set risk sensitivity (e.g., conservative, moderate, lenient).
	AI-Generated Contract Summary (Easy understanding)
For user convenience, the AI provides a concise summary of key contract clauses.
→ Provides a summary report before signing
Focuses on clauses that typically cause disputes or confusion
Converts complex legal language into easy-to-understand sentences
→ Provides a PDF download of summaries and actual contracts

Web page configuration

1. Contract Home (C-1)
Introduction Area
Introduction to "AI Automatic Contract Generator"
→ AI automatically creates customized class contracts and guides you through risk clauses.
Contract Creation Section
[Teacher's choice drop-down]
[Select class type drop-down] (Short term, long term, group class, etc.)
[Enter class details]
→ Date, time, place, etc
[Contract preview button]
[Contract creation button]
Electronic Signature Introduction Banner
→ The electronic signature guarantees legal effectiveness.

🔹2. Contract Preview (C-2)
Contract Summary Section
Summary list of key provisions (recommendation of visual card form)
 → For example:
class information
Cost and Refund Policy
class cancellation regulations
Duties of instructors and students
Personal Information Protection
a dispute settlement method
[Look at the full contract button]
[Download PDF button]
[Electronic signature button]
🔹 3. AI Contract Risk Clause Warning (C-3)
Risk Detection Summary Section
"Potential risk provisions detected by AI" box
User Risk Sensitivity Settings Toggle (Conservative/Medium/Generous)
List of detected risk clauses
Clause title
Risk Summary
Why it could be a problem
Recommendation Modification Statement Example
[Apply modification button]

🔹4. Contract Edit/Regenerate Area (C-4)
Enter custom modification requests window
 → "Please change the refund conditions more flexibly", etc
[Reply request]
Real-time Revision Reflected Contract Preview

🔹5. Contract Management My Page (C-5)
a list of my contracts
Status display (creating / signing complete / modifying)
Date created, class information summary
View Contract, Modify, Save PDF, Delete button
Check contract signing history


Write only for a contract based on this guideline and this JSON data.
'''

def ask_ai_to_manage2(json_data):
    global message_contract
    system_prompt = message_contract

    messages = [
        {"role": "user", "content": system_prompt},
        {"role": "user", "content": f"JSON Data:\n{json_data}"},
    ]

    response = client.chat.completions.create(
        model="gpt-4.1-nano",
        messages=messages
    )

    return (response.choices[0].message.content)

response_buffer = ""

def chatbot(request):
    userinfo = request.session.get('response')
    if request.method == 'POST':
        message = request.POST.get('message')
        db = load_db("./chatbot/project.json")
        response = ask_ai_to_manage(db, userinfo, message)
        request.session['response'] = response
        return redirect('project')
    return render(request, 'chatbot.html')

def project(request):
    response = request.session.get('response')
    return render(request, 'project.html', {'response': response})

def contract(request):
    response = request.session.get('response')

    new_response = ask_ai_to_manage2(response)

    return render(request, 'contract.html', {'new_response': new_response})

def login(request):
    
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = auth.authenticate(request, username = username, password = password)
        if user is not None:
            auth.login(request, user)
            request.session['response'] = {'username': user.username, 'userjob': user.email}
            return redirect('chatbot')
        else:
            error_message = 'Invalid username or password!'
            return render(request, 'login.html', {'error_message': error_message})
    else:
        return render(request, 'login.html')

def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        jobinfo = request.POST['jobinfo']
        jobexplain = request.POST['jobexplain']

        if password1 == password2:
            try:
                user = User.objects.create_user(username=username, email=jobinfo+", "+jobexplain, password=password1)
                user.save()
                return redirect('login')
            
            except Exception as e:
                print("exception:", e)
                error_message = 'Error creating account'
                return render(request, 'register.html', {'error_message': error_message})
        else:
            error_message = 'Passwords do not match!'
            return render(request, 'register.html', {'error_message': error_message})

    return render(request, 'register.html')

def logout(request):
    auth.logout(request)

def project_register(request):
    return render(request, 'project_register.html')