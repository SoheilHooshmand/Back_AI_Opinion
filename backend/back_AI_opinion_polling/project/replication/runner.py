"""
Human-sampling pipeline integrated with your Django models:

1) Read SiliconePerson rows for a Project.
2) Read a Question for that Project.
3) Build prompts (backstory + question + options).
4) Call GPT (Chat Completions) with logprobs to simulate "votes".
5) Collapse first-token logprobs to candidate-level probabilities (soft).
6) Save Prompt, Response, and ModelLog rows.
7) Return approximate total cost in USD.
"""

from typing import Dict, List, Sequence, Tuple, Union
import os
from django.db import transaction
from django.db.models import QuerySet
from openai import OpenAI

from project.models import Project, SiliconePerson, Prompt, Question, Response, ModelLog, Cost
from .common import (
    collapse_token_sets_soft,
    estimate_prompt_cost_usd,
    count_tokens,
    get_default_token_sets,
    extract_probs_from_top_logprobs
)

MODEL_NAME = os.getenv("GPT_MODEL")

INPUT_PRICE_PER_1K = 0.0006
OUTPUT_PRICE_PER_1K = 0.0024

MAX_OUTPUT_TOKENS = 3
TOP_LOGPROBS = 20



def build_backstory(person: SiliconePerson) -> str:
    """
    Turn a SiliconePerson row into a natural-language backstory.
    You can tweak the wording as needed.
    """
    parts: List[str] = []

    if person.age is not None:
        parts.append(f"You are a {person.age}-year-old")
    else:
        parts.append("You are a")

    if person.gender:
        parts.append(person.gender.lower())

    if person.education:
        parts.append(f"with {person.education.lower()} education")

    sentence = " ".join(parts).strip()
    if person.state:
        sentence += f" living in {person.state}"

    sentence = sentence.strip() + "."

    extras = []

    if person.race:
        extras.append(f"Your race is: {person.race}.")
    if person.party:
        extras.append(f"You identify with the {person.party} party.")
    if person.ideology:
        extras.append(f"Your political ideology is {person.ideology}.")
    if person.political_interest:
        extras.append(f"Your interest in politics is described as: {person.political_interest}.")
    if person.discuss_politics:
        extras.append(f"You discuss politics: {person.discuss_politics}.")
    if person.church_goer:
        extras.append(f"You attend church: {person.church_goer}.")
    if person.religion:
        extras.append(f"Your religion is {person.religion}.")
    if person.financially:
        extras.append(f"Financially, you feel: {person.financially}.")
    if person.patriotism:
        extras.append(f"Your level of patriotism is: {person.patriotism}.")

    if person.more_info:
        for k, v in person.more_info.items():
            extras.append(f"{k.replace('_', ' ').capitalize()}: {v}")

    backstory = " ".join([sentence] + extras)
    return backstory.strip()


def build_prompt(backstory: str, question_text: str, options: List[str]) -> str:
    """
    Build the final prompt for one SiliconePerson.
    """
    lines = [
        backstory.strip(),
        "",
        question_text.strip(),
        "",
        "Possible answers:",
    ]
    for i, opt in enumerate(options, start=1):
        lines.append(f"{i}. {opt}")
    lines.append("")
    lines.append("IMPORTANT:")
    lines.append("Your answer MUST contain ONLY the candidate's name, exactly as written above.")
    lines.append("Do NOT write anything else. Do NOT explain. Do NOT add punctuation.")
    lines.append("Return ONLY the name. Example of correct format: obama")
    lines.append("Example of INCORRECT format: 'I would vote for Obama.'")
    return "\n".join(lines)




def create_client() -> OpenAI:
    """
    Create an OpenAI client. Requires OPENAI_API_KEY in env.
    """
    return OpenAI(api_key=os.environ["OPENAI_API_KEY"])


def call_model_with_logprobs(
    client: OpenAI,
    model_name: str,
    prompt: str,
    max_output_tokens: int = MAX_OUTPUT_TOKENS,
    top_logprobs: int = TOP_LOGPROBS,
    temperature: float = 0.0,
) -> Tuple[Dict[str, float], str, int]:
    """
    Call the Chat Completions API and return:
      - token_logprobs: dict[token -> logprob] for the first output token
      - raw_text: full generated text
      - tokens_used: total tokens (input + output)
    """
    response = client.chat.completions.create(
        model=model_name,
        messages=[
            {"role": "user", "content": prompt},
        ],
        max_tokens=max_output_tokens,
        logprobs=True,
        top_logprobs=top_logprobs,
        temperature=temperature,
    )

    choice = response.choices[0]

    raw_text = choice.message.content

    lp_info = choice.logprobs
    first_token_info = lp_info.content[0]
    top = first_token_info.top_logprobs  # list of logprob objects

    token_logprobs = {item.token: float(item.logprob) for item in top}

    tokens_used = None
    try:
        if hasattr(response, "usage") and response.usage is not None:
            if hasattr(response.usage, "total_tokens"):
                tokens_used = int(response.usage.total_tokens)
            elif hasattr(response.usage, "prompt_tokens") and hasattr(
                response.usage, "completion_tokens"
            ):
                tokens_used = int(
                    response.usage.prompt_tokens + response.usage.completion_tokens
                )
    except Exception:
        tokens_used = None

    if tokens_used is None:
        tokens_used = count_tokens(prompt, model_name) + max_output_tokens

    return token_logprobs, raw_text, tokens_used



def candidate_probs_from_logprobs(
    token_logprobs: Dict[str, float],
    token_sets: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    1) token_logprobs -> normalized probs over tokens
    2) collapse → candidate-level (soft token-set collapse)
    """

    token_probs = extract_probs_from_top_logprobs(token_logprobs)
    candidate_probs = collapse_token_sets_soft(token_probs, token_sets)
    return candidate_probs


def argmax_key(d: Dict[str, float]) -> str:
    """
    Return the key with the highest value in a dict.
    """
    if not d:
        return ""
    return max(d.items(), key=lambda kv: kv[1])[0]




def estimate_total_cost_for_prompts(
    prompts: Sequence[str],
    model_name: str,
    input_price_per_1k: float,
    output_price_per_1k: float,
    max_output_tokens: int,
) -> float:
    """
    Estimate total API cost for a list of prompts.
    """
    total_cost = 0.0
    for p in prompts:
        total_cost += estimate_prompt_cost_usd(
            prompt=p,
            model_name=model_name,
            input_price_per_1k=input_price_per_1k,
            max_output_tokens=max_output_tokens,
            output_price_per_1k=output_price_per_1k,
        )
    return float(total_cost)




@transaction.atomic
def run_human_sampling_for_project(
    project: Union[int, Project, QuerySet],
    question: Union[int, Question, QuerySet],
    token_sets: Dict[str, List[str]],
    model_name: str = MODEL_NAME,
    temperature: float = 0.0,
    just_cost: bool = False,
) -> float:
    """
    Main entry:

    - project: Project instance, project id, or QuerySet[Project]
    - question: Question instance, question id, or QuerySet[Question]
    - token_sets: dict[candidate_name -> list of lexical tokens]
                  (e.g., DEFAULT_TOKEN_SETS_2016)
    """

    if isinstance(project, QuerySet):
        project = project.get()
    elif isinstance(project, int):
        project = Project.objects.get(id=project)

    if isinstance(question, QuerySet):
        question = question.get()
    elif isinstance(question, int):
        question = Question.objects.get(id=question, project=project)

    project_obj: Project = project
    question_obj: Question = question

    persons: List[SiliconePerson] = list(
        SiliconePerson.objects.filter(project=project_obj)
    )

    question_text = question_obj.body
    options = list(token_sets.keys())

    prompts: List[str] = []
    for person in persons:
        backstory = build_backstory(person)
        prompt_text = build_prompt(backstory, question_text, options)
        prompts.append(prompt_text)
    total_cost = estimate_total_cost_for_prompts(
        prompts=prompts,
        model_name=model_name,
        input_price_per_1k=INPUT_PRICE_PER_1K,
        output_price_per_1k=OUTPUT_PRICE_PER_1K,
        max_output_tokens=MAX_OUTPUT_TOKENS,
    )
    if just_cost:
        return total_cost
    Cost.objects.create(
        project=project_obj,
        question=question_obj,
        total_cost=total_cost,
    )

    client = create_client()

    for person, prompt_text in zip(persons, prompts):
        Prompt.objects.create(
            project=project_obj,
            body=prompt_text,
            question=question_obj,
            silicone_person=person,
        )

        token_logprobs, raw_text, tokens_used = call_model_with_logprobs(
            client=client,
            model_name=model_name,
            prompt=prompt_text,
            max_output_tokens=MAX_OUTPUT_TOKENS,
            top_logprobs=TOP_LOGPROBS,
            temperature=temperature,
        )

        candidate_probs = candidate_probs_from_logprobs(token_logprobs, token_sets)
        predicted_choice = argmax_key(candidate_probs)
        confidence = candidate_probs.get(predicted_choice, None) if predicted_choice else None

        Response.objects.create(
            question=question_obj,
            silicone_person=person,
            raw_response=raw_text,
            structured_data={
                "token_logprobs": token_logprobs,
                "candidate_probs": candidate_probs,
                "predicted_choice": predicted_choice,
                "options": options,
            },
            confidence_score=confidence,
            gpt_model=model_name,
        )

        ModelLog.objects.create(
            project=project_obj,
            silicone_person=person,
            prompt_text=prompt_text,
            response_text=raw_text,
            model_name=model_name,
            tokens_used=tokens_used,
            temperature=temperature,
        )

    return total_cost




def run(project, question, year):
    token_sets = get_default_token_sets(year)
    cost = run_human_sampling_for_project(
        project=project.id,
        question=question.id,
        token_sets=token_sets,
        model_name=MODEL_NAME,
        temperature=0.0,
    )
    return cost
