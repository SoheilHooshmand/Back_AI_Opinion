from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from drf_spectacular.utils import (
    extend_schema,
    OpenApiResponse,
    OpenApiParameter,
    OpenApiExample,
)
from drf_spectacular.types import OpenApiTypes
from .searializer import (
    CreateProjectSerializer,
    ProjectListSerializer,
    CreateSiliconPersonsSerializer,
    SiliconPersonListSerializer,
    CreateQuestionSerializer,
    QuestionListSerializer,
    SiliconPersonCSVUploadSerializer,
    TokenCostSerializer,
    QuestionsCSVUploadSerializer,
)
from .models import(
    Project,
    SiliconePerson,
    Question,
    Response as ResponseModel,
    AnalysisResult,
)
from loguru import logger
from django.db import IntegrityError
from .tasks import ask_gpt
import csv
import io
import os
from .replication.runner import run_human_sampling_for_project
from .replication.common import get_default_token_sets
from .utils import calculate_simulation_cost, parse_questions_file, MODEL_PRICING
from django.shortcuts import get_object_or_404
from django.db.models import Case, When, Value, CharField, Count, F, ExpressionWrapper, IntegerField
from django.db.models.functions import Cast, Coalesce





class ProjectView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Project"],
        summary="List user projects",
        description="Retrieve all projects created by the authenticated user. Each project will contain basic details such as title, description, and creation date.",
        responses=ProjectListSerializer(many=True),
    )
    def get(self, request):
        try:
            user = request.user
            projects = Project.objects.filter(user=user)
            serializer = ProjectListSerializer(projects, many=True)
            response = {"data": serializer.data, "status": status.HTTP_200_OK}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["Project"],
        summary="Create a new project",
        description="Create a new project for the authenticated user. The project title must be unique per user.",
        request=CreateProjectSerializer,
        responses={
            201: CreateProjectSerializer,
            400: OpenApiResponse(description="Duplicate project title"),
        }
    )
    def post(self, request):
        data = request.data
        serializer = CreateProjectSerializer(data=data)
        if serializer.is_valid(raise_exception=True):
            try:
                user = request.user
                pr = Project.objects.create(user=user,
                                       title=serializer.validated_data['title'],
                                       description=serializer.validated_data['description'],
                                       )
                data = serializer.validated_data
                data['project_id'] = pr.id
                response = {"data": data, "status": status.HTTP_201_CREATED}
                return Response(data=response, status=status.HTTP_201_CREATED)
            except IntegrityError:
                title = serializer.validated_data['title']
                return Response(
                    {'error': f"A project with the title '{title}' already exists for this user."},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(str(e))
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class SiliconPersonView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Silicon Person"],
        summary="List silicon persons in a project",
        description="Retrieve all silicon persons associated with a given project. You must provide the `project_id` as a query parameter.",
        parameters=[
            OpenApiParameter(
                name="project_id",
                type=int,
                required=True,
                location=OpenApiParameter.QUERY,
                description="Project ID"
            )
        ],
        responses=SiliconPersonListSerializer(many=True),
    )
    def get(self, request):
        project_id = request.query_params.get('project_id', None)
        if not project_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'erroe': 'Missing required parameter: project_id'})
        try:
            project = Project.objects.get(id=project_id)
            if project.user != request.user:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'Unauthorized access'})
            silicon_persons = SiliconePerson.objects.filter(project=project)
            serializer = SiliconPersonListSerializer(silicon_persons, many=True)
            response = {"data": serializer.data, "status": status.HTTP_200_OK}
            return Response(response, status=status.HTTP_200_OK)
        except Exception as e:
            logger.error(str(e))
            return Response(status=status.HTTP_400_BAD_REQUEST)


    @extend_schema(
        tags=["Silicon Person"],
        summary="Create silicon persons",
        description="Add multiple silicon persons to a project. Accepts a list of silicon person details.",
        request=CreateSiliconPersonsSerializer,
        responses=CreateSiliconPersonsSerializer
    )
    def post(self, request):
        serializer = CreateSiliconPersonsSerializer(data=request.data)
        user = request.user
        if serializer.is_valid(raise_exception=True):
            try:
                project_id = serializer.validated_data['project_id']
                persons_data = serializer.validated_data['siliconpersons']

                try:
                    project = Project.objects.get(id=project_id)
                except Project.DoesNotExist:
                    return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Project not found!'})

                if project.user != user:
                    return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You are not the owner of this project!'})


                persons_to_create = [
                    SiliconePerson(project=project, **person_data)
                    for person_data in persons_data
                ]
                SiliconePerson.objects.bulk_create(persons_to_create)
                response = {"data": serializer.validated_data, "status": status.HTTP_201_CREATED}
                return Response(
                    response,
                    status=status.HTTP_201_CREATED
                )
            except Project.DoesNotExist:
                return Response(
                    {"error": "Project not found.", "status": status.HTTP_404_NOT_FOUND},
                    status=status.HTTP_404_NOT_FOUND
                )
            except Exception as e:
                logger.error(str(e))
                return Response(
                    {"error": "Internal server error.", "status": status.HTTP_500_INTERNAL_SERVER_ERROR},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class SamplingViews(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Sampling"],
        summary="Get a question",
        description="Retrieve a specific question by ID. Only accessible if the question belongs to a project owned by the authenticated user.",
        parameters=[
            OpenApiParameter("question_id", int, required=True, location="query")
        ],
        responses=QuestionListSerializer
    )
    def get(self, request):
        user = request.user
        question_id = request.query_params.get('question_id', None)
        if not question_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'erroe': 'Missing required parameter: question_id'})
        try:
            question = Question.objects.get(id=question_id)
            if question.project.user != user:
                return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You cannot access projects of other users.'})
            serializer = QuestionListSerializer(question)
            response = {"data": serializer.data, "status": status.HTTP_200_OK}
            return Response(response, status=status.HTTP_200_OK)
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Question not found.'})
        except Exception as e:
            logger.error(str(e))
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @extend_schema(
        tags=["Sampling"],
        summary="Create a sampling question",
        description="Create a new question under a project. This endpoint calculates the estimated cost of human sampling for the question.",
        request=CreateQuestionSerializer,
        responses=CreateQuestionSerializer
    )
    def post(self, request):
        user = request.user
        serializer = CreateQuestionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                project = Project.objects.get(id=serializer.validated_data['project_id'])
            except Project.DoesNotExist:
                return Response(
                    {'error': 'Project not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if project.user != user:
                return Response(
                    {'error': 'You cannot access projects of other users.'},
                    status=status.HTTP_403_FORBIDDEN
                )
                
            model_name = serializer.validated_data.get('model_name')
            if model_name:
                # Validate provided model
                if model_name not in MODEL_PRICING:
                    return Response(
                        {'error': f"Invalid model_name. Supported models: {', '.join(MODEL_PRICING.keys())}"},
                        status=status.HTTP_400_BAD_REQUEST
                    )
            else:
                # Use default from env if not provided
                model_name = os.getenv("GPT_MODEL")

            try:
                real_answer = serializer.validated_data.get('real_answer')
                question = Question.objects.create(
                    project=project,
                    body=serializer.validated_data['body'],
                    real_answer=real_answer,
                    model_name=model_name
                )

                response_serializer = CreateQuestionSerializer(question)
                project.status = 'draft'
                project.save()
                year = 0
                if project.id == 1:
                    year = 2016
                elif project.id == 3:
                    year = 2012
                elif project.id == 4:
                    year = 2020
                token_sets = get_default_token_sets(year)
                cost = run_human_sampling_for_project(project=project.id, question=question.id, token_sets=token_sets,
                                                      just_cost=True)
                response_data = response_serializer.data.copy()
                response_data['cost'] = cost
                response = {"data": response_data, "status": status.HTTP_201_CREATED}
                return Response(response, status=status.HTTP_201_CREATED)

            except IntegrityError as e:
                logger.error(f"IntegrityError creating question: {e}")
                return Response(
                    {'error': 'A question with this body already exists for the project.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Unexpected error creating question: {e}")
                return Response(
                    {'error': 'Failed to create question.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )


class ModelResponseView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Model"],
        summary="Get model response for a question",
        description="Fetch model-generated responses for a given question and project. Accessible only if the project belongs to the user and the question has been completed.",
        parameters=[
            OpenApiParameter("project_id", int, required=True, location="query"),
            OpenApiParameter("question_id", int, required=True, location="query"),
        ],
        responses=OpenApiResponse(
            response={
                "type": "object",
                "properties": {
                    "data": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "question": {"type": "string"},
                                "silicon_person_id": {"type": "integer"},
                                "response_of_model": {"type": "string"},
                            }
                        }
                    },
                    "status": {"type": "integer"}
                }
            }
        )
    )
    def get(self, request):
        user = request.user
        project_id = request.query_params.get('project_id', None)
        question_id = request.query_params.get('question_id', None)
        if not question_id and not project_id:
            return Response(status=status.HTTP_400_BAD_REQUEST, data={'erroe': 'Missing required parameter'})
        try:
            project = Project.objects.get(id=project_id)
            question = Question.objects.get(id=question_id)
        except Project.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Project not found.'})
        except Question.DoesNotExist:
            return Response(status=status.HTTP_404_NOT_FOUND, data={'error': 'Question not found.'})
        if project.user != user:
            return Response(status=status.HTTP_403_FORBIDDEN, data={'error': 'You cannot access projects of other users.'})
        if project.status != 'completed' and not question.gpt_answer:
            return Response(status=status.HTTP_200_OK, data={'message': 'mission did not complete!'})
        silicon_persons = SiliconePerson.objects.filter(project=project)
        responses = ResponseModel.objects.filter(silicone_person__in=silicon_persons, question=question)
        output = {"data": [], "status": 200}
        for response in responses:
            output["data"].append({
                "question": question.body,
                "silicon_person_id": response.silicone_person.id,
                "response_of_model": response.raw_response,
            })
        return Response(output, status=status.HTTP_200_OK)



class QuickAnswerView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Model"],
        summary="Get a quick GPT answer",
        description="Generate a quick GPT response for a question. The answer is processed asynchronously using Celery.",
        request=CreateQuestionSerializer,
        responses=CreateQuestionSerializer
    )
    def post(self, request):
        user = request.user
        serializer = CreateQuestionSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            try:
                project = Project.objects.get(id=serializer.validated_data['project_id'])
            except Project.DoesNotExist:
                return Response(
                    {'error': 'Project not found.'},
                    status=status.HTTP_404_NOT_FOUND
                )

            if project.user != user:
                return Response(
                    {'error': 'You cannot access projects of other users.'},
                    status=status.HTTP_403_FORBIDDEN
                )

            try:
                real_answer = serializer.validated_data.get('real_answer')
                question = Question.objects.create(
                    project=project,
                    body=serializer.validated_data['body'],
                    real_answer=real_answer
                )

                response_serializer = CreateQuestionSerializer(question)
                project.status = 'draft'
                project.save()
                ask_gpt.delay(question.id)
                response = {"data": response_serializer.data, "status": status.HTTP_201_CREATED}
                return Response(response, status=status.HTTP_201_CREATED)
            except IntegrityError as e:
                logger.error(f"IntegrityError creating question: {e}")
                return Response(
                    {'error': 'A question with this body already exists for the project.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            except Exception as e:
                logger.error(f"Unexpected error creating question: {e}")
                return Response(
                    {'error': 'Failed to create question.'},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR
                )




class SiliconPersonByCSV(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Silicon Person"],
        summary="Upload silicon persons via CSV",
        description="Upload a CSV file to create multiple silicon persons for a given project. The CSV should contain the required fields for each person.",
        request=SiliconPersonCSVUploadSerializer,
        responses={
            201: OpenApiResponse(
                description="CSV imported successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "created_count": {"type": "integer"},
                        "ids": {"type": "array", "items": {"type": "integer"}}
                    }
                }
            ),
            400: OpenApiResponse(description="Bad request"),
            404: OpenApiResponse(description="Project not found"),
        }
    )
    def post(self, request):
        file = request.FILES.get('silicon_persons')
        project_id = request.data.get('project_id')

        if not file:
            return Response({"error": "CSV file 'silicon_person' is required"}, status=400)

        if not project_id:
            return Response({"error": "project_id is required"}, status=400)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        try:
            decoded_file = file.read().decode('utf-8')
        except:
            return Response({"error": "Unable to decode CSV file"}, status=400)

        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created_objects = []

        for row in reader:
            fields = {
                "project": project,
                "id_str": row.get("id", None),
                "name": row.get("name", None),
                "race": row.get("race", None),
                "discuss_politics": row.get("discuss_politics", None),
                "ideology": row.get("ideology", None),
                "party": row.get("party", None),
                "church_goer": row.get("church_goer", None),
                "gender": row.get("gender", None),
                "age": row.get("age", None),
                "political_interest": row.get("political_interest", None),
                "state": row.get("state", None),
                "religion": row.get("religion", None),
                "education": row.get("education", None),
                "financially": row.get("financially", None),
                "patriotism": row.get("patriotism", None),
                "real_vote": row.get("real_vote", None),
                "more_info": row.get("more_info", None),
            }
            obj = SiliconePerson.objects.create(**fields)
            created_objects.append(obj.id)

        return Response({
            "message": "Silicone persons imported successfully.",
            "created_count": len(created_objects),
            "ids": created_objects
        }, status=status.HTTP_201_CREATED)





class AnalyseResultsView(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Project"],
        summary="Get analysis result by question",
        description="Retrieve analysis results for a specific question, including accuracy metrics, Cohen's kappa, entropy, correlations, and collapsed probabilities by silicon person.",
        parameters=[
            OpenApiParameter(
                "question_id",
                int,
                required=True,
                location=OpenApiParameter.QUERY,
                description="ID of the question to fetch analysis for"
            ),
        ],
        responses={
            200: OpenApiResponse(
                description="Analysis result retrieved successfully",
                response={
                    "type": "object",
                    "properties": {
                        "data": {
                            "type": "object",
                            "properties": {
                                "n": {"type": "integer"},
                                "accuracy": {"type": "number"},
                                "project_id": {"type": "integer"},
                                "question_id": {"type": "integer"},
                                "cohens_kappa": {"type": "number"},
                                "entropy_mean": {"type": "number"},
                                "positive_label": {"type": "string"},
                                "phi_correlation_est": {"type": "number"},
                                "pearson_corr_real_vs_predprob": {"type": "number"},
                                "mutual_info_template_output_mean": {"type": "number"},
                                "collapsed_probs_by_person": {
                                    "type": "object",
                                    "additionalProperties": {
                                        "type": "object",
                                        "properties": {
                                            "obama": {"type": "number"},
                                            "romney": {"type": "number"}
                                        }
                                    }
                                }
                            }
                        },
                        "status": {"type": "integer"}
                    }
                }
            ),
            400: OpenApiResponse(description="Missing or invalid question_id"),
            404: OpenApiResponse(description="Result not found"),
            500: OpenApiResponse(description="Unexpected internal server error"),
        }
    )
    def get(self, request):
        question_id = request.query_params.get('question_id', None)
        if question_id is None:
            return Response({"error": "Project or Question ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            question_id = int(question_id)
        except ValueError:
            return Response({"error": "Invalid project ID"}, status=status.HTTP_400_BAD_REQUEST)
        try:
            result = AnalysisResult.objects.get(question__id=question_id)
            response = {"data" : {}, "status":status.HTTP_200_OK}
            response['data'] = result.result_data
            return Response(response, status=status.HTTP_200_OK)
        except AnalysisResult.DoesNotExist:
            return Response({"error": "not found"}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            logger.error(f"Unexpected error getting analysis result: {e}")
            return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class QuestionImportByCSV(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        tags=["Question"],
        summary="Upload questions via CSV",
        description="Upload a CSV file to create multiple questions for a given project. "
                    "CSV must include at least a 'body' column.",
        request=QuestionsCSVUploadSerializer,
        responses={
            201: OpenApiResponse(
                description="CSV imported successfully",
                response={
                    "type": "object",
                    "properties": {
                        "message": {"type": "string"},
                        "created_count": {"type": "integer"},
                        "ids": {"type": "array", "items": {"type": "integer"}}
                    }
                }
            ),
            400: OpenApiResponse(description="Bad request"),
            404: OpenApiResponse(description="Project not found"),
        }
    )
    def post(self, request):
        file = request.FILES.get('questions')
        project_id = request.data.get('project_id')
        
        model_name_input = request.data.get('model_name')
        final_model_name = None

        if model_name_input:
            # Validate provided model
            if model_name_input not in MODEL_PRICING:
                return Response(
                    {"error": f"Invalid model_name. Supported models: {', '.join(MODEL_PRICING.keys())}"},
                    status=status.HTTP_400_BAD_REQUEST
                )
            final_model_name = model_name_input
        else:
            # Use default from env if not provided
            final_model_name = os.getenv("GPT_MODEL")

        if not file:
            return Response({"error": "CSV file 'questions' is required"}, status=400)

        if not project_id:
            return Response({"error": "project_id is required"}, status=400)

        try:
            project = Project.objects.get(id=project_id)
        except Project.DoesNotExist:
            return Response({"error": "Project not found"}, status=404)

        try:
            decoded_file = file.read().decode('utf-8')
        except:
            return Response({"error": "Unable to decode CSV file"}, status=400)

        io_string = io.StringIO(decoded_file)
        reader = csv.DictReader(io_string)

        created_ids = []


        for row in reader:
            question_data = {
                "project": project,
                "body": row.get("body"),
                "real_answer": row.get("real_answer") or None,
                "gpt_answer": False,
                "is_analysed": False,
                "model_name": final_model_name
            }

            # "body" is mandatory
            if not question_data["body"]:
                return Response({
                    "error": "Each row must include a 'body' field."
                }, status=400)

            obj = Question.objects.create(**question_data)
            created_ids.append(obj.id)
            project.status='draft'
            project.save()

        return Response({
            "message": "Questions imported successfully.",
            "created_count": len(created_ids),
            "ids": created_ids
        }, status=status.HTTP_201_CREATED)


class TokenCostEstimationView(APIView):
    """
    Stateless endpoint to estimate simulation costs.
    Calculates: Cost = (Standard Person Token + Question Token) * N People
    Uses standard_response for unified API output.
    """
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    @extend_schema(
        tags=["Estimation"],
        summary="Estimate token cost for simulation",
        description="Estimate the token cost for simulating responses based on the provided model, questions, and number of silicon people.",
        request=TokenCostSerializer,
        responses={
            200: OpenApiResponse(
                description="Token cost estimation calculated successfully",
                response={
                    "type": "object",
                    "properties": {
                        "success": {"type": "boolean"},
                        "message": {"type": "string"},
                        "data": {
                            "type": "object",
                            "properties": {
                                "model": {"type": "string"},
                                "simulation_details": {
                                    "type": "object",
                                    "properties": {
                                        "num_silicon_people": {"type": "integer"},
                                        "num_questions": {"type": "integer"},
                                        "total_requests": {"type": "integer"}
                                        }
                                },
                                "tokens":{ 
                                    "type": "object",
                                    "properties": {
                                        "input": {"type": "integer"},
                                        "output": {"type": "integer"}
                                        }
                                },
                                "cost_usd": {
                                    "type": "object",
                                    "properties": {
                                        "input": {"type": "number", "format": "float"},
                                        "output": {"type": "number", "format": "float"},
                                        "total": {"type": "number", "format": "float"}
                                        }
                                }
                            }
                        },
                        "status_code": {"type": "integer"},
                        "code": {"type": "string"},
                        }
                    }
                ),
            400: OpenApiResponse(description="Validation failed"),
            500: OpenApiResponse(description="Internal calculation error")
            }
    )
    
    def post(self, request):
        serializer = TokenCostSerializer(data=request.data)
        if not serializer.is_valid():
            # Standard Error Response for Validation Failures
            return standard_response(
                success=False,
                message="Validation failed.",
                data=serializer.errors,
                code="invalid_input",
                status_code=status.HTTP_400_BAD_REQUEST
            )

        data = serializer.validated_data
        
        try:
            # 1. Extract Questions Strategy
            if data.get('questions_file'):
                questions = parse_questions_file(data['questions_file'])
            else:
                questions = data['questions_list']

            if not questions:
                # Standard Error Response for Logic Failure (Empty Questions)
                return standard_response(
                    success=False,
                    message="No questions found in the provided source.",
                    code="missing_questions",
                    status_code=status.HTTP_400_BAD_REQUEST
                )

            # 2. Calculate Logic
            result = calculate_simulation_cost(
                model_name=data['model_name'],
                questions=questions,
                num_people=data['num_silicon_people']
            )
            
            # Standard Success Response with Calculation Data
            return standard_response(
                success=True,
                message="Token cost estimation calculated successfully.",
                data=result,
                status_code=status.HTTP_200_OK
            )

        except ValueError as e:
            # Standard Error Response for Expected User Errors (e.g. bad file format)
            return standard_response(
                success=False,
                message=str(e),
                code="value_error",
                status_code=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            # Standard Error Response for Unexpected System Errors
            return standard_response(
                success=False,
                message="Internal calculation error.",
                data={"details": str(e)},
                code="internal_error",
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

def standard_response(data=None, success=True, message=None, code=None, status_code=status.HTTP_200_OK):
    """
    Universal helper function to standardize API responses across the project.
    
    Format:
    {
        "success": True/False,
        "message": "Optional message",
        "data": { ... } or [ ... ],
        "code": "error_code" (optional, typically for errors)
        "status_code": 200 (The explicit HTTP status code in the body)
    }
    
    Args:
        data (any): The main payload (dict, list, string, etc.). Defaults to {} if None.
        success (bool): operational success status. Defaults to True.
        message (str, optional): Summary message. Removed from response if None.
        code (str|int, optional): Error code or specific application code.
        status_code (int): HTTP status code for the response. Defaults to 200.
        
    Returns:
        Response: A Django REST Framework Response object with the standardized payload.
    """
    response_payload = {
        "success": success,
        "data": data if data is not None else {},
        "status_code": status_code # Explicitly include the HTTP status code in the body
    }

    # Add message only if provided
    if message:
        response_payload["message"] = message

    # Add code only if provided (usually for tracking specific errors)
    if code is not None:
        response_payload["code"] = code

    return Response(response_payload, status=status_code)


@extend_schema(
    tags=["User Statistics"],
    summary="Get demographic statistics for a project",
    description="""Retrieve demographic statistics for all silicon people in a specific project.

**Requires Authentication:** Yes
**Permissions:** User must own the project

Returns counts grouped by:
- Gender
- Race
- Ideology
- Party
- State
- Political Interest
- Political Discussion Frequency
- Church Attendance
- Age Groups
- Patriotism Level
- Real Vote History

Empty or null values are automatically converted to "unknown" in the response.
Age values are grouped into ranges for better analysis.
""",
    parameters=[
        OpenApiParameter(
            name="project_id",
            type=OpenApiTypes.INT,
            location=OpenApiParameter.QUERY,
            required=True,
            description="ID of the project to get statistics for",
            examples=[
                OpenApiExample(
                    "Example Project ID",
                    value=123
                )
            ]
        )
    ],
    responses={
        200: OpenApiResponse(
            description="Statistics retrieved successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True
                    },
                    "message": {
                        "type": "string",
                        "example": "Statistics retrieved successfully"
                    },
                    "data": {
                        "type": "object",
                        "properties": {
                            "gender": {
                                "type": "object",
                                "description": "Counts by gender",
                                "example": {
                                    "male": 1500,
                                    "female": 1200,
                                    "other": 300,
                                    "unknown": 52
                                }
                            },
                            "race": {
                                "type": "object",
                                "description": "Counts by race",
                                "example": {
                                    "white": 1800,
                                    "black": 700,
                                    "asian": 350,
                                    "hispanic": 200,
                                    "unknown": 100
                                }
                            },
                            "ideology": {
                                "type": "object",
                                "description": "Counts by political ideology",
                                "example": {
                                    "liberal": 1000,
                                    "conservative": 900,
                                    "moderate": 800,
                                    "unknown": 52
                                }
                            },
                            "party": {
                                "type": "object",
                                "description": "Counts by political party",
                                "example": {
                                    "democrat": 1100,
                                    "republican": 950,
                                    "independent": 700,
                                    "unknown": 52
                                }
                            },
                            "state": {
                                "type": "object",
                                "description": "Counts by US state",
                                "example": {
                                    "CA": 500,
                                    "TX": 450,
                                    "NY": 400,
                                    "FL": 350,
                                    "unknown": 52
                                }
                            },
                            "political_interest": {
                                "type": "object",
                                "description": "Counts by political interest level",
                                "example": {
                                    "high": 1200,
                                    "medium": 900,
                                    "low": 700,
                                    "unknown": 52
                                }
                            },
                            "discuss_politics": {
                                "type": "object",
                                "description": "Frequency of political discussion",
                                "example": {
                                    "daily": 800,
                                    "weekly": 1200,
                                    "monthly": 700,
                                    "rarely": 500,
                                    "never": 300,
                                    "unknown": 52
                                }
                            },
                            "church_goer": {
                                "type": "object",
                                "description": "Church attendance frequency",
                                "example": {
                                    "weekly": 1000,
                                    "monthly": 800,
                                    "yearly": 600,
                                    "never": 700,
                                    "unknown": 52
                                }
                            },
                            "age": {
                                "type": "object",
                                "description": "Counts by age groups (ranges)",
                                "example": {
                                    "18-24": 500,
                                    "25-34": 800,
                                    "35-44": 700,
                                    "45-54": 600,
                                    "55-64": 500,
                                    "65+": 400,
                                    "unknown": 52
                                }
                            },
                            "patriotism": {
                                "type": "object",
                                "description": "Level of patriotism",
                                "example": {
                                    "very_patriotic": 1000,
                                    "somewhat_patriotic": 900,
                                    "neutral": 800,
                                    "not_very_patriotic": 500,
                                    "not_at_all_patriotic": 300,
                                    "unknown": 52
                                }
                            },
                            "real_vote": {
                                "type": "object",
                                "description": "Real voting history in elections",
                                "example": {
                                    "always": 1200,
                                    "usually": 900,
                                    "sometimes": 700,
                                    "rarely": 500,
                                    "never": 400,
                                    "unknown": 52
                                }
                            }
                        }
                    },
                    "status_code": {
                        "type": "integer",
                        "example": 200
                    },
                    "code": {
                        "type": "string",
                        "example": "STATISTICS_RETRIEVED"
                    }
                }
            }
        ),
        400: OpenApiResponse(
            description="Bad Request - Missing or invalid parameters",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "project_id is required"},
                    "status_code": {"type": "integer", "example": 400},
                    "code": {"type": "string", "example": "MISSING_PARAMETER"}
                }
            }
        ),
        401: OpenApiResponse(
            description="Unauthorized - Invalid authentication or project ownership",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "This project does not belong to you."},
                    "status_code": {"type": "integer", "example": 401},
                    "code": {"type": "string", "example": "UNAUTHORIZED_ACCESS"}
                }
            }
        ),
        404: OpenApiResponse(
            description="Project not found",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "Project not found"},
                    "status_code": {"type": "integer", "example": 404},
                    "code": {"type": "string", "example": "PROJECT_NOT_FOUND"}
                }
            }
        )
    },
    examples=[
        OpenApiExample(
            "Successful Response",
            value={
                "success": True,
                "message": "Statistics retrieved successfully",
                "data": {
                    "gender": {
                        "male": 1987,
                        "female": 2231,
                        "unknown": 52
                    },
                    "race": {
                        "white": 2500,
                        "black": 800,
                        "asian": 450,
                        "hispanic": 350,
                        "unknown": 100
                    },
                    "ideology": {
                        "liberal": 1500,
                        "conservative": 1400,
                        "moderate": 1200,
                        "unknown": 170
                    },
                    "party": {
                        "democrat": 1600,
                        "republican": 1300,
                        "independent": 900,
                        "unknown": 270
                    },
                    "state": {
                        "CA": 600,
                        "TX": 500,
                        "NY": 450,
                        "FL": 400,
                        "unknown": 130
                    },
                    "political_interest": {
                        "high": 1800,
                        "medium": 1200,
                        "low": 800,
                        "unknown": 270
                    },
                    "discuss_politics": {
                        "daily": 800,
                        "weekly": 1200,
                        "monthly": 700,
                        "rarely": 500,
                        "never": 300,
                        "unknown": 270
                    },
                    "church_goer": {
                        "weekly": 1000,
                        "monthly": 800,
                        "yearly": 600,
                        "never": 700,
                        "unknown": 270
                    },
                    "age": {
                        "18-24": 500,
                        "25-34": 800,
                        "35-44": 700,
                        "45-54": 600,
                        "55-64": 500,
                        "65+": 400,
                        "unknown": 270
                    },
                    "patriotism": {
                        "very_patriotic": 1000,
                        "somewhat_patriotic": 900,
                        "neutral": 800,
                        "not_very_patriotic": 500,
                        "not_at_all_patriotic": 300,
                        "unknown": 270
                    },
                    "real_vote": {
                        "always": 1200,
                        "usually": 900,
                        "sometimes": 700,
                        "rarely": 500,
                        "never": 400,
                        "unknown": 270
                    }
                },
                "status_code": 200,
                "code": "STATISTICS_RETRIEVED"
            },
            response_only=True,
            status_codes=['200']
        ),
        OpenApiExample(
            "Unauthorized Access",
            value={
                "success": False,
                "message": "This project does not belong to you.",
                "status_code": 401,
                "code": "UNAUTHORIZED_ACCESS"
            },
            response_only=True,
            status_codes=['401']
        )
    ],
    auth=["Bearer"],
    operation_id="get_user_statistics",
    deprecated=False
)
class UserStatistics(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get('project_id')
        user = request.user

        project = get_object_or_404(Project, id=project_id)
        if project.user != user:
            return standard_response(
                success=False,
                message="This project does not belong to you.",
                status_code=status.HTTP_401_UNAUTHORIZED
            )

        silicon_people = SiliconePerson.objects.filter(project=project)
        data = {}

        def get_counts(field_name):
            if field_name == 'age':
                # Special handling for age field with multiple conditions
                return silicon_people.annotate(
                    display_value=Case(
                        # First handle null values
                        When(age__isnull=True, then=Value("unknown")),
                        # Handle if age field might be CharField with empty string
                        When(age__exact="", then=Value("unknown")),
                        # Handle if age is 0 or negative
                        When(age__lte=0, then=Value("unknown")),
                        # Convert valid numeric age to string
                        default=Cast('age', CharField()),
                        output_field=CharField()
                    )
                ).values('display_value').annotate(
                    count=Count('id')
                )
            else:
                # Standard handling for text fields
                return silicon_people.annotate(
                    display_value=Case(
                        When(**{f"{field_name}__exact": ""}, then=Value("unknown")),
                        When(**{f"{field_name}__isnull": True}, then=Value("unknown")),
                        default=field_name,
                        output_field=CharField()
                    )
                ).values('display_value').annotate(
                    count=Count('id')
                )

        fields = ['gender', 'race', 'ideology', 'party', 'state', 'political_interest',
                  'discuss_politics', 'church_goer', 'age', 'patriotism', 'real_vote']

        for field in fields:
            try:
                counts = get_counts(field)
                data[field] = {
                    item['display_value']: item['count']
                    for item in counts
                }
            except Exception as e:
                # Log the error for debugging
                import logging
                logger = logging.getLogger(__name__)
                logger.error(f"Error retrieving {field} statistics: {str(e)}")

                # Try alternative method
                data[field] = self._get_counts_alternative(silicon_people, field)

        return standard_response(
            success=True,
            message="Statistics retrieved successfully",
            data=data,
            status_code=status.HTTP_200_OK,
            code="STATISTICS_RETRIEVED"
        )

    def _get_counts_alternative(self, queryset, field_name):
        """Alternative method to get counts if the main method fails"""
        try:
            if field_name == 'age':
                # Manual aggregation for age
                age_data = {}
                unknown_count = 0

                for person in queryset.only('age'):
                    age = getattr(person, 'age')

                    # Check if age is valid
                    if age is None or age == "":
                        unknown_count += 1
                    elif isinstance(age, (int, float)) and age > 0:
                        age_str = str(int(age))
                        age_data[age_str] = age_data.get(age_str, 0) + 1
                    else:
                        unknown_count += 1

                if unknown_count > 0:
                    age_data['unknown'] = unknown_count

                return age_data

            else:
                # For other fields, use Python aggregation
                field_data = {}
                for person in queryset.only(field_name):
                    value = getattr(person, field_name)
                    if value is None or value == "":
                        value = "unknown"
                    field_data[value] = field_data.get(value, 0) + 1

                return field_data

        except Exception as e:
            return {"error": f"Could not retrieve {field_name} statistics"}


@extend_schema(
    tags=["AI Models"],
    summary="Get available AI models",
    description="""Retrieve a list of all available AI models that can be used for simulations.

**Features:**
- Returns a curated list of supported AI models
- Includes various model sizes and versions (nano, mini, turbo, pro)
- Models are ready-to-use for silicon people simulations
- Updated regularly with new model releases

**Authentication:** Required (Bearer Token)

**Usage:** Use these model names when configuring simulations or estimating token costs.
""",
    responses={
        200: OpenApiResponse(
            description="AI models retrieved successfully",
            response={
                "type": "object",
                "properties": {
                    "success": {
                        "type": "boolean",
                        "example": True,
                        "description": "Indicates if the request was successful"
                    },
                    "message": {
                        "type": "string",
                        "example": "AI models retrieved successfully",
                        "description": "Success message"
                    },
                    "data": {
                        "type": "array",
                        "description": "List of available AI model identifiers",
                        "items": {
                            "type": "string",
                            "enum": [
                                "gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-pro",
                                "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o",
                                "gpt-4o-mini", "gpt-3.5-turbo"
                            ]
                        },
                        "example": [
                            "gpt-5.1", "gpt-5", "gpt-5-mini", "gpt-5-nano", "gpt-5-pro",
                            "gpt-4.1", "gpt-4.1-mini", "gpt-4.1-nano", "gpt-4o",
                            "gpt-4o-mini", "gpt-3.5-turbo"
                        ]
                    },
                    "status_code": {
                        "type": "integer",
                        "example": 200,
                        "description": "HTTP status code"
                    },
                    "code": {
                        "type": "string",
                        "example": "AI_MODELS_RETRIEVED",
                        "description": "Internal response code"
                    }
                }
            }
        ),
        401: OpenApiResponse(
            description="Unauthorized - Authentication required",
            response={
                "type": "object",
                "properties": {
                    "success": {"type": "boolean", "example": False},
                    "message": {"type": "string", "example": "Authentication credentials were not provided."},
                    "status_code": {"type": "integer", "example": 401},
                    "code": {"type": "string", "example": "AUTHENTICATION_REQUIRED"}
                }
            }
        )
    },
    examples=[
        OpenApiExample(
            "Successful Response",
            value={
                "success": True,
                "message": "AI models retrieved successfully",
                "data": [
                    "gpt-5.1",
                    "gpt-5",
                    "gpt-5-mini",
                    "gpt-5-nano",
                    "gpt-5-pro",
                    "gpt-4.1",
                    "gpt-4.1-mini",
                    "gpt-4.1-nano",
                    "gpt-4o",
                    "gpt-4o-mini",
                    "gpt-3.5-turbo"
                ],
                "status_code": 200,
                "code": "AI_MODELS_RETRIEVED"
            },
            response_only=True,
            status_codes=['200']
        )
    ],
    auth=["Bearer"],
    operation_id="get_ai_models",
    deprecated=False
)
class AImodels(APIView):
    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Get available AI models",
        description="Returns a list of all supported AI models for simulations."
    )
    def get(self, request):
        return standard_response(
            success=True,
            message="AI models retrieved successfully",
            data=[
                'gpt-5.1', 'gpt-5', 'gpt-5-mini', 'gpt-5-nano', 'gpt-5-pro',
                'gpt-4.1', 'gpt-4.1-mini', 'gpt-4.1-nano', 'gpt-4o',
                'gpt-4o-mini', 'gpt-3.5-turbo'
            ],
            status_code=status.HTTP_200_OK,
            code="AI_MODELS_RETRIEVED"
        )