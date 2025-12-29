from celery import shared_task
from loguru import logger
from .models import Project, Question
from .replication.postprocessor import compute_metrics_for_project, save_metrics_to_db
from .replication.runner import run

@shared_task
def ask_gpt(question_id=None):
    """
    Replacement ask_gpt that uses the replication runner (Completion API + logprobs).
    """
    try:
        if question_id:
            questions = Question.objects.filter(id=question_id)
        else:
            projects = Project.objects.filter(status="draft")
            questions = Question.objects.filter(project__in=projects,  gpt_answer=False)

        for question in questions:
            if question.gpt_answer:
                continue

            project = question.project
            project.status = "running"
            project.save()

            logger.info(f"[RUN] Starting replication for project {project.id}")

            year = ""
            if project.id == 1:
                year = 2016
            elif project.id == 3:
                year = 2012
            elif project.id == 4:
                year = 2020
            cost = run(project, question, year)
            logger.info(f"[RUN] Completed replication for question {question.id} and cost is {cost}")
            question.gpt_answer = True
            question.save()

            qs = project.questions.all()
            completed_check = True
            for q in qs:
                if not q.gpt_answer:
                    completed_check = False
                    break
            if completed_check:
                project.status = "completed"
                project.save()
            logger.info(f"[DONE] Replication completed for project {project.id}")

    except Exception as e:
        logger.error(f"[ask_gpt ERROR] {e}")
        project = question.project
        project.status = "failed"
        project.save()

    return {"status": "ok"}

@shared_task
def analysis_results():

    summary = {
        "projects_analyzed": 0,
        "results_created": 0,
    }

    try:
        questions = Question.objects.filter(is_analysed=False, gpt_answer=True)
        for question in questions:
            project = question.project
            logger.info(f"[POSTPROCESS] Project {project.id}")

            metrics = compute_metrics_for_project(project_id=project.id, question_id=question.id)

            if "error" in metrics:
                logger.warning(f"[SKIP] Project {project.id}: {metrics['error']}")
                continue

            save_metrics_to_db(project.id, metrics)
            summary["projects_analyzed"] += 1
            summary["results_created"] += 1

            logger.info(f"[SAVED] AnalysisResult for project {project.id}")
            question.is_analysed=True
            question.save()
    except Exception as e:
        logger.error(f"[analysis_results ERROR] {e}")

    return summary