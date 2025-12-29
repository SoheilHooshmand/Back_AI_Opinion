import math
from typing import Tuple, Dict, Any, Union, List, Optional

import numpy as np
import pandas as pd
from scipy.stats import pearsonr
from sklearn.metrics import cohen_kappa_score, matthews_corrcoef

from project.models import Project, SiliconePerson, Question, Response, AnalysisResult




PROJECT_CONFIG: Dict[int, Dict[str, Union[int, str]]] = {
    3: {"year": 2012, "positive_label": "obama"},
    1: {"year": 2016, "positive_label": "trump"},
    4: {"year": 2020, "positive_label": "biden"},
}


def get_project_config(project_id: int) -> Tuple[int, str]:
    """
    Return (year, positive_label) for a given project_id.
    """
    if project_id not in PROJECT_CONFIG:
        raise ValueError(f"Unknown project_id {project_id}. Update PROJECT_CONFIG.")
    cfg = PROJECT_CONFIG[project_id]
    return int(cfg["year"]), str(cfg["positive_label"]).strip().lower()



def clean_nan_to_none(data: Union[float, Any]) -> Union[float, None, Any]:
    if isinstance(data, float) and np.isnan(data):
        return None
    return data


def entropy_from_probs(probs: Dict[str, float]) -> float:
    """
    Entropy of a categorical distribution given as a dict {label: p}
    (natural log, as in Argyle's Postprocessor).
    """
    arr = np.array(list(probs.values()), dtype=float)
    arr = arr[arr > 0]
    if len(arr) == 0:
        return 0.0
    return -float(np.sum(arr * np.log(arr)))


def binary_entropy(p: float) -> float:
    """Binary entropy H_b(p) = -[p ln p + (1-p) ln(1-p)]."""
    if p <= 0.0 or p >= 1.0:
        return 0.0
    return -(p * math.log(p) + (1 - p) * math.log(1 - p))


def agg_prob_dicts(dicts: List[Dict[str, float]]) -> Dict[str, float]:
    """
    Argyle-style aggregation (Postprocessor.agg_prob_dicts):
    average a list of probability dicts elementwise.
    """
    n = len(dicts)
    agg: Dict[str, float] = {}
    if n == 0:
        return agg
    for d in dicts:
        for k, v in d.items():
            agg[k] = agg.get(k, 0.0) + float(v) / n
    return agg


def calculate_conditional_entropy(df: pd.DataFrame) -> pd.DataFrame:
    """
    Adds 'conditional_entropy' column: H(Y|X=x) = entropy of row['collapsed_probs'].
    Mirrors Postprocessor.calculate_conditional_entropy.
    """
    df = df.copy()
    df["conditional_entropy"] = df["collapsed_probs"].apply(entropy_from_probs)
    return df


def get_marginal_distribution(df: pd.DataFrame, groupby: str = "question_id") -> pd.DataFrame:
    """
    Computes marginal distributions over categories, grouped by 'groupby'.
    Mirrors Postprocessor.get_marginal_distribution (using 'question_id').
    """
    grouped = df.groupby(by=groupby)["collapsed_probs"].agg(agg_prob_dicts)
    marginal_df = pd.DataFrame(grouped)
    marginal_df.rename(columns={"collapsed_probs": "probs"}, inplace=True)
    return marginal_df


def calculate_mutual_information_template_output(
    df: pd.DataFrame, groupby: str = "question_id"
) -> pd.DataFrame:
    """
    Argyle-style MI: between 'template' (here question_id) and output distribution.

    Uses H(Y) - H(Y|X):
      - H(Y|X=x) from row-wise entropies of probs (collapsed_probs)
      - H(Y) from entropies of aggregated distributions per group
    """
    df = calculate_conditional_entropy(df)

    marginal_df = get_marginal_distribution(df, groupby=groupby)

    marginal_df["entropy"] = marginal_df["probs"].apply(entropy_from_probs)

    def mutual_inf_row(row):
        idx = row[groupby]
        H_Y_group = marginal_df.loc[idx]["entropy"]
        H_Y_given_x = row["conditional_entropy"]
        return float(H_Y_group - H_Y_given_x)

    df["mutual_inf"] = df.apply(mutual_inf_row, axis=1)
    return df




def normalize_real_vote_label(raw_vote: str, year: int) -> Optional[str]:
    """
    Map raw real_vote string to canonical label for a given year.

    Returns:
        - "obama", "romney", "trump", "clinton", "biden", "other"
        - None if the case should be treated as missing (Inapplicable, Refused, Missing, etc.)
    """
    if not raw_vote:
        return None

    rv = raw_vote.strip().lower()

    missing_markers = [
        "missing, no vote for pres",
        "no vote for pres",
        "no vote for president",
        "did not vote for pres",
        "did not report vote for pres",
        "did not report vote",
        "did not report",
        "post/no post",
        "no post-election data",
        "inapplicable",
        "refused",
    ]
    for m in missing_markers:
        if m in rv:
            return None

    if year == 2012:
        if "obama" in rv:
            return "obama"
        if "romney" in rv:
            return "romney"
        if rv.startswith("other"):
            return "other"
        return None

    if year == 2016:
        if "donald" in rv and "trump" in rv:
            return "trump"
        if "hillary" in rv and "clinton" in rv:
            return "clinton"
        if "jill" in rv and "stein" in rv:
            return "other"
        if "gary" in rv and "johnson" in rv:
            return "other"
        if "other candidate" in rv:
            return "other"
        return None

    if year == 2020:
        if "donald" in rv and "trump" in rv:
            return "trump"
        if "joe" in rv and "biden" in rv:
            return "biden"
        if "jo jorgensen" in rv:
            return "other"
        if "howie" in rv and "hawkins" in rv:
            return "other"
        return None

    return None



def compute_metrics_for_project(project_id: int, question_id: int) -> Dict[str, Any]:
    """
    Compute metrics for all Responses in a project.

    - Applies “missing / refused / inapplicable” logic:
        such cases are excluded from the analysis (real_vote_label = None).
    - For VALID cases:
        a prediction is correct iff canonical predicted label == canonical real label.
    """
    project = Project.objects.get(id=project_id)
    year, positive_label = get_project_config(project_id)
    positive_label_normalized = positive_label.strip().lower()

    responses = (
        Response.objects.filter(question_id=question_id)
        .select_related("silicone_person", "question")
    )

    rows = []

    for r in responses:
        person = r.silicone_person
        struct = r.structured_data or {}

        collapsed = (
            struct.get("collapsed_probs")
            or struct.get("candidate_probs")
            or {}
        )
        token_probs = (
            struct.get("token_probs")
            or struct.get("token_logprobs")
            or {}
        )

        if not collapsed:
            continue

        real_vote_raw = (person.real_vote or "").strip()
        real_label = normalize_real_vote_label(real_vote_raw, year)

        if real_label is None:
            continue

        raw_response = (r.raw_response or "").strip().lower()

        pred_label = struct.get("predicted_choice")
        if not pred_label:
            pred_label = max(collapsed.keys(), key=lambda k: collapsed[k])
        pred_label_norm = pred_label.strip().lower()

        pred_pos = float(collapsed.get(positive_label_normalized, 0.0))

        real_vote_pos = 1 if real_label == positive_label_normalized else 0

        is_correct = 1 if pred_label_norm == real_label else 0

        row = {
            "response_id": r.id,
            "question_id": r.question.id,
            "person_id": person.id,
            "real_vote_raw": real_vote_raw,
            "real_vote": real_label,
            "real_vote_pos": real_vote_pos,
            "pred_label": pred_label_norm,
            "pred_pos": pred_pos,
            "raw_response": raw_response,
            "accuracy": is_correct,
            "entropy": entropy_from_probs(collapsed),
            "collapsed_probs": collapsed,
            "token_probs": token_probs,
            "positive_label": positive_label_normalized,
        }
        rows.append(row)

    if len(rows) == 0:
        return {"error": "no processed responses with usable ground truth found for project"}

    df = pd.DataFrame(rows)

    # Binary prediction: is model's positive prob > 0.5?
    df["pred_vote_dichot"] = df["pred_pos"].apply(lambda p: 1 if p > 0.50 else 0)

    # Pearson correlation between real positive (0/1) and predicted positive prob
    if df["real_vote_pos"].nunique() > 1:
        corr_pearson, pval_pearson = pearsonr(df["real_vote_pos"], df["pred_pos"])
    else:
        corr_pearson, pval_pearson = float("nan"), float("nan")

    # Cohen's kappa and Matthews phi on 0/1 labels
    if df["real_vote_pos"].nunique() > 1 and df["pred_vote_dichot"].nunique() > 1:
        kappa = cohen_kappa_score(df["real_vote_pos"], df["pred_vote_dichot"])
        corr_phi = matthews_corrcoef(df["real_vote_pos"], df["pred_vote_dichot"])
    else:
        kappa = float("nan")
        corr_phi = float("nan")

    # Argyle-style MI between template (question) and output distribution
    df = calculate_mutual_information_template_output(df, groupby="question_id")
    mutual_info_template_output = float(df["mutual_inf"].mean())

    # Extra: mutual information between real positive (Y) and model p_hat (X)
    p_y = df["real_vote_pos"].mean()
    H_Y = binary_entropy(p_y)

    def cond_entropy_binary_row(row):
        p_hat = float(row["pred_pos"])
        return binary_entropy(p_hat)

    df["cond_entropy_binary"] = df.apply(cond_entropy_binary_row, axis=1)
    H_Y_given_X = float(df["cond_entropy_binary"].mean())
    mutual_info_real_vs_predprob = H_Y - H_Y_given_X

    metrics = {
        "n": int(len(df)),
        "accuracy_mean": clean_nan_to_none(float(df["accuracy"].mean())),
        "entropy_mean": clean_nan_to_none(float(df["entropy"].mean())),
        "mutual_info_template_output_mean": clean_nan_to_none(mutual_info_template_output),
        "mutual_info_real_vs_predprob": clean_nan_to_none(mutual_info_real_vs_predprob),
        "pearson_corr_predprob_vs_realvote": clean_nan_to_none(float(corr_pearson)),
        "pearson_pval": clean_nan_to_none(float(pval_pearson)),
        "cohens_kappa": clean_nan_to_none(float(kappa)),
        "phi_correlation_est": clean_nan_to_none(float(corr_phi)),
        "df": df,
    }

    return metrics


def save_metrics_to_db(project_id: int, metrics: Dict[str, Any]) -> None:
    """
    Saves per-question aggregates into AnalysisResult.

    IMPORTANT:
      - Uses update_or_create so you get at most ONE row per (question, method).
    """
    year, positive_label = get_project_config(project_id)
    df: pd.DataFrame = metrics["df"]

    for qid, group in df.groupby("question_id"):
        accuracy = float(group["accuracy"].mean())
        entropy_mean = float(group["entropy"].mean())

        if group["real_vote_pos"].nunique() > 1 and group["pred_pos"].nunique() > 1:
            pred_corr_pearson, _ = pearsonr(group["real_vote_pos"], group["pred_pos"])
        else:
            pred_corr_pearson = float("nan")

        # Kappa and phi
        if group["real_vote_pos"].nunique() > 1 and group["pred_vote_dichot"].nunique() > 1:
            kappa = cohen_kappa_score(group["real_vote_pos"], group["pred_vote_dichot"])
            corr_phi = matthews_corrcoef(group["real_vote_pos"], group["pred_vote_dichot"])
        else:
            kappa = float("nan")
            corr_phi = float("nan")

        # Argyle-style MI (template vs output) on this question
        mutual_info_template_output = float(group["mutual_inf"].mean())

        # store collapsed probs per person for inspection
        collapsed_by_person = {
            int(row.person_id): row.collapsed_probs
            for _, row in group.iterrows()
        }

        data = {
            "project_id": int(project_id),
            "question_id": int(qid),
            "n": int(len(group)),
            "accuracy": clean_nan_to_none(accuracy),
            "entropy_mean": clean_nan_to_none(entropy_mean),
            "pearson_corr_real_vs_predprob": clean_nan_to_none(pred_corr_pearson),
            "cohens_kappa": clean_nan_to_none(kappa),
            "phi_correlation_est": clean_nan_to_none(corr_phi),
            "positive_label": positive_label,
            "mutual_info_template_output_mean": clean_nan_to_none(mutual_info_template_output),
            "collapsed_probs_by_person": collapsed_by_person,
        }

        AnalysisResult.objects.update_or_create(
            question_id=qid,
            method="gpt_vote_replication",
            defaults={
                "parameters": {"positive_label": positive_label, "year": year},
                "result_data": data,
            },
        )
