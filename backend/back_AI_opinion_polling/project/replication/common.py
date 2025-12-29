from typing import Dict, List
import numpy as np
import tiktoken

def lc(t: str) -> str:
    return t.lower()


def uc(t: str) -> str:
    return t.upper()


def mc(t: str) -> str:
    tmp = t.lower()
    return tmp[0].upper() + tmp[1:] if tmp else tmp


def gen_variants(toks: List[str]) -> List[str]:
    """
    Generate simple variants of each token, as in the paper:
    - lower-case
    - UPPER-CASE
    - Capitalized
    and prefix each with a leading space.

    Example:
        ["trump"] -> [" trump", " TRUMP", " Trump"]
    """
    results: List[str] = []
    variants = [lc, uc, mc]
    for t in toks:
        for v in variants:
            results.append(" " + v(t))
    return results


DEFAULT_TOKEN_SETS_2012: Dict[str, List[str]] = {
    "romney": gen_variants(["romney", "mitt", "republican", "conservative"]),
    "obama": gen_variants(["obama", "barack", "democrat", "democratic", "liberal"]),
}

DEFAULT_TOKEN_SETS_2016: Dict[str, List[str]] = {
    "trump": gen_variants(["trump", "donald", "republican", "conservative"]),
    "clinton": gen_variants(["clinton", "hillary", "rodham", "democrat", "liberal"]),
}

DEFAULT_TOKEN_SETS_2020: Dict[str, List[str]] = {
    "trump": gen_variants(["donald", "trump", "republican", "conservative"]),
    "biden": gen_variants(["joe", "biden", "democrat", "liberal"]),
}


def get_default_token_sets(year: int) -> Dict[str, List[str]]:
    """
    Helper to pick the right token sets by election year.
    """
    if year == 2012:
        return DEFAULT_TOKEN_SETS_2012
    if year == 2016:
        return DEFAULT_TOKEN_SETS_2016
    if year == 2020:
        return DEFAULT_TOKEN_SETS_2020
    raise ValueError(f"No default token sets defined for year {year}")




def logsumexp_norm(log_probs: Dict[str, float]) -> Dict[str, float]:
    """
    Convert a dict of log-probabilities to normalized probabilities
    using log-sum-exp.

    Input:
        {" token": logprob, ...}
    Output:
        {" token": prob, ...} with probs summing to 1.0
    """
    if not log_probs:
        return {}

    arr = np.array(list(log_probs.values()), dtype=float)
    maxv = float(np.max(arr))
    exps = np.exp(arr - maxv)
    probs = exps / float(exps.sum())
    keys = list(log_probs.keys())
    return {keys[i]: float(probs[i]) for i in range(len(keys))}


def extract_probs_from_top_logprobs(top_logprobs: Dict[str, float]) -> Dict[str, float]:
    """
    Accepts a top_logprobs dict (token -> logprob) and returns normalized probs.
    """
    return logsumexp_norm(top_logprobs)



def collapse_r(probs: Dict[str, float], toks: List[str]) -> float:
    """
    Study 2-style "collapse_r": sum probabilities for an exact list of tokens.
    """
    total_prob = 0.0
    for t in toks:
        if t in probs:
            total_prob += float(probs[t])
    return float(total_prob)


def collapse_token_sets_exact(
    probs: Dict[str, float],
    token_sets: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    Collapse token-level probabilities into candidate-level probabilities,
    following the exact Study 2 (GPT-3) code in Argyle et al.
    """
    sums = {cat: collapse_r(probs, toks) for cat, toks in token_sets.items()}
    s = sum(sums.values())
    if s <= 0:
        return {k: 0.0 for k in sums}
    return {k: v / s for k, v in sums.items()}


def collapse_token_sets_soft(
    probs: Dict[str, float],
    token_sets: Dict[str, List[str]],
) -> Dict[str, float]:
    """
    Soft collapse:
    - lowercase + strip normalization
    - prefix / reverse-prefix / substring matching
    - spreads probability mass across candidates ⇒ non-binary scores.
    """
    new_d = {cat: 1e-12 for cat in token_sets.keys()}

    for tok, p in probs.items():
        tok_norm = tok.lower().strip()
        if not tok_norm:
            continue

        for cat, toks in token_sets.items():
            for t in toks:
                t_norm = t.lower().strip()
                if not t_norm:
                    continue


                if (
                    tok_norm.startswith(t_norm)
                    or t_norm.startswith(tok_norm)
                    or (t_norm in tok_norm)
                ):
                    new_d[cat] += p
                    break

    Z = sum(new_d.values())
    if Z == 0:
        return {k: 0.0 for k in new_d}
    return {k: v / Z for k, v in new_d.items()}


def collapse_token_sets(
    probs: Dict[str, float],
    token_sets: Dict[str, List[str]],
    matching_strategy: str = "soft",
) -> Dict[str, float]:
    """
    Wrapper so old imports still work:

    matching_strategy:
      - "exact": Study 2-style exact collapse
      - "soft":  soft collapse (default, recommended)
    """
    if matching_strategy == "exact":
        return collapse_token_sets_exact(probs, token_sets)
    if matching_strategy == "soft":
        return collapse_token_sets_soft(probs, token_sets)
    raise ValueError(f"Unknown matching_strategy: {matching_strategy}")




def get_encoding_for_model(model_name: str):
    """
    Returns the tiktoken encoding object for the given OpenAI model name.
    """
    try:
        return tiktoken.encoding_for_model(model_name)
    except KeyError:
        return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str, model_name: str) -> int:
    """
    Count tokens in a piece of text for a given model using tiktoken.
    """
    enc = get_encoding_for_model(model_name)
    return len(enc.encode(text))


def estimate_prompt_cost_usd(
    prompt: str,
    model_name: str,
    input_price_per_1k: float,
    max_output_tokens: int,
    output_price_per_1k: float,
) -> float:
    """
    Rough cost estimate for ONE prompt:

    cost = (input_tokens / 1000 * input_price) + (max_output_tokens / 1000 * output_price)
    """
    n_in = count_tokens(prompt, model_name)
    in_cost = (n_in / 1000.0) * input_price_per_1k
    out_cost = (max_output_tokens / 1000.0) * output_price_per_1k
    return float(in_cost + out_cost)
