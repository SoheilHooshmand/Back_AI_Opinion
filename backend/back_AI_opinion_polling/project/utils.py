from .models import *
import openai
from dotenv import load_dotenv
import os
from loguru import logger
import pandas as pd

import json
import csv
import io
from django.shortcuts import get_object_or_404
from .replication.common import count_tokens, estimate_prompt_cost_usd
from .replication.runner import build_backstory, build_prompt
from .models import SiliconePerson

load_dotenv()

def ask_from_gpt():
    api_key = os.getenv("OPENAI_API_KEY")
    openai.api_key = api_key
    client = openai.OpenAI(api_key=api_key)
    question = Question.objects.first()
    slic_per1 = SiliconePerson.objects.get(id=1)
    slic_per2 = SiliconePerson.objects.get(id=2)
    slic_per3 = SiliconePerson.objects.get(id=3)
    slic_per4 = SiliconePerson.objects.get(id=4)
    slic_per5 = SiliconePerson.objects.get(id=5)
    slic_per6 = SiliconePerson.objects.get(id=6)
    persons = [slic_per1, slic_per2, slic_per3, slic_per4, slic_per5, slic_per6]
    total_prompt_tokens = 0
    total_completion_tokens = 0

    for person in persons:
        prompt = Prompt.objects.first().body
        if person.skin_color is not None:
            prompt = prompt.replace('{skin_color}', person.skin_color)
        else:
            prompt = prompt.replace('Racially, I am {skin_color}.', '')

        if person.political_orientation is not None and person.ideological is not None:
            prompt = prompt.replace(
                '{politically or ideologically or both of them}',
                f'Ideologically, I am {person.ideological}. Politically, I am a/an {person.political_orientation}'
            )
        elif person.political_orientation is not None:
            prompt = prompt.replace(
                '{politically or ideologically or both of them}',
                f'Politically, I am a/an {person.political_orientation}'
            )
        elif person.ideological is not None:
            prompt = prompt.replace(
                '{politically or ideologically or both of them}',
                f'Ideologically, I am {person.ideological}'
            )
        else:
            prompt = prompt.replace(
                '{politically or ideologically or both of them}',
                ''
            )
        if person.age is not None:
            prompt = prompt.replace('{age}', str(person.age))
        else:
            prompt = prompt.replace('I am {age}.', '')
        if person.gender is not None:
            prompt = prompt.replace('{gender}', str(person.gender))
        else:
            prompt = prompt.replace('i am a {gender}.', '')
        if person.state is not None:
            prompt = prompt.replace('{state}', str(person.state))
        else:
            prompt = prompt.replace('I am from {state}.', '')
        if person.more_info is not None:
            prompt = prompt.replace('{more info}', str(person.more_info))
        else:
            prompt = prompt.replace('{more info}', '')

        prompt += "\n" + question.body
        prompt += ( '\nBy default, the percentages should sum to 100.'
                    '\nFinal answer must be in this format and not extra things or description:'
                   '\nProbability of voting for Trump: ?\nProbability of voting for Clinton: ?')
        gpt_model = os.getenv("GPT_MODEL")
        gpt_response = client.chat.completions.create(
            model=gpt_model,
            temperature=0,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        answer = gpt_response.choices[0].message.content
        total_prompt_tokens += gpt_response.usage.prompt_tokens
        total_completion_tokens += gpt_response.usage.completion_tokens
        Response.objects.create(
            question=question,
            silicone_person=person,
            raw_response=answer,
            gpt_model=gpt_model,
        )
        logger.info(f"process of person {person.id}\nprompt: {prompt}")
    total_tokens = total_prompt_tokens + total_completion_tokens
    total_cost_usd = (total_prompt_tokens / 1000) * 0.0015 + (total_completion_tokens / 1000) * 0.002
    logger.info(f"Total prompt tokens used: {total_prompt_tokens}")
    logger.info(f"Total completion tokens used: {total_completion_tokens}")
    logger.info(f"Total tokens used: {total_tokens}")
    logger.info(f"Approximate cost in USD: ${total_cost_usd:.6f}")
    logger.info('all process finished!')


# Pricing dictionary for popular models (Prices per 1K tokens in USD)
MODEL_PRICING = {
    "gpt-5.1": {"input": 1.25, "output": 10.00},
    "gpt-5": {"input": 1.25, "output": 10.00},
    "gpt-5-mini": {"input": 0.25, "output": 2.00},
    "gpt-5-nano": {"input": 0.05, "output": 0.40},
    "gpt-5-pro": {"input": 15.00, "output": 120.00},
    "gpt-4.1": {"input": 2.00, "output": 8.00},
    "gpt-4.1-mini": {"input": 0.40, "output": 1.60},
    "gpt-4.1-nano": {"input": 0.10, "output": 0.40},
    "gpt-4o": {"input": 2.50, "output": 10.00},
    "gpt-4o-mini": {"input": 0.15, "output": 0.60},
    "gpt-3.5-turbo": {"input": 0.50, "output": 1.50},
    # Legacy/Other models can be added here
}


def parse_questions_file(uploaded_file):
    """
    Parses TXT, CSV, or Excel file into a list of question strings.
    Assumes questions are in the first column for structured files.
    """
    try:          
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file, header=None)
        elif uploaded_file.name.endswith(('.xls', '.xlsx')):
            df = pd.read_excel(uploaded_file, header=None)
        else:
            raise ValueError("Unsupported file format. Please upload .txt, .csv, .xls, or .xlsx.")
        
        # Take the first column as questions
        if not df.empty:
            return df.iloc[:, 0].astype(str).tolist()
        return []
        
    except Exception as e:
        raise ValueError(f"Error parsing file: {str(e)}")

def get_standard_backstory_text():
    """
    Generates a standard backstory text.
    If a real person exists in DB, uses it.
    Otherwise, creates a fully-populated dummy person based on runner.py attributes
    to ensure token estimation reflects a complete profile.
    """
    person = SiliconePerson.objects.first()
    
    if not person:
        # Create an unsaved dummy person with ALL attributes used in build_backstory
        person = SiliconePerson(
            age=45,
            gender="Female",
            education="College Graduate",
            state="Pennsylvania", # Represents an avg length state name
            race="White",
            party="Independent",
            ideology="Moderate",
            political_interest="Very Interested",
            discuss_politics="Frequently",
            church_goer="Weekly",
            religion="Protestant",
            financially="Comfortable",
            patriotism="Very Patriotic"
            # 'more_info' can be left empty or added if needed for max buffer
        )
        
    return build_backstory(person)

def calculate_simulation_cost(model_name, questions, num_people):
    """
    Calculates cost by: 
    (Backstory + Question + Template Tokens) * Num_People * Price
    """
    pricing = MODEL_PRICING.get(model_name)
    if not pricing:
        raise ValueError(f"Model {model_name} not supported.")

    # 1. Get the base backstory (Constant part)
    backstory_text = get_standard_backstory_text()
    
    # Dummy options are required for build_prompt to generate the full template instructions
    dummy_options = ["Option A", "Option B"]

    total_in_tokens = 0
    total_out_tokens = 0
    
    # 2. Iterate over questions
    for question_text in questions:
        # Build full prompt using the exact logic from runner.py
        # This includes the "IMPORTANT: ..." instructions which add tokens
        full_text = build_prompt(backstory_text, question_text, dummy_options)
        
        # Count tokens for ONE person answering THIS question
        tokens_per_person = count_tokens(full_text, model_name)
        
        # Multiply by number of silicon people requested
        total_in_tokens += (tokens_per_person * num_people)
        
        # Estimate output tokens (e.g. "Option A" or candidate name) per person
        total_out_tokens += (3 * num_people)

    # 3. Calculate Final Price
    input_cost = (total_in_tokens / 1000000) * pricing['input'] * 1.20
    output_cost = (total_out_tokens / 1000000) * pricing['output'] * 1.20
    total_cost = input_cost + output_cost

    return {
        "model": model_name,
        "simulation_details": {
            "num_silicon_people": num_people,
            "num_questions": len(questions),
            "total_requests": num_people * len(questions)
        },
        "tokens": {"input": total_in_tokens, "output": total_out_tokens},
        "cost_usd": {
            "input": round(input_cost, 6),
            "output": round(output_cost, 6),
            "total": round(total_cost, 6)
        }
    }