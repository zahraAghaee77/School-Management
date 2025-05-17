from drf_yasg.utils import swagger_auto_schema
from rest_framework import status, viewsets
from rest_framework.decorators import *
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework.views import *

from school.models import *
from user.models import *

from .models import *
from .permission import *
from .serializer import *


class AssignmentViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Assignment.objects.all().order_by("created_at")
    serializer_class = AssignmentSerializer

    def get_permissions(self):
        if self.action == "create":
            permission_classes = [IsTeacherOfLesson]
        elif self.action in ["update", "partial_update"]:
            permission_classes = [CanUpdateAssignment]
        else:
            permission_classes = [IsAuthenticated]

        return [permission() for permission in permission_classes]

    def get_queryset(self):
        user = self.request.user

        if user.user_type == "teacher":
            return Assignment.objects.filter(class_obj__teacher=user).order_by(
                "created_at"
            )

        elif user.user_type == "student":
            return Assignment.objects.filter(class_obj__students=user).order_by(
                "created_at"
            )

        return Assignment.objects.none()

    def get_serializer_class(self):
        if self.action in ["update", "partial_update", "create"]:
            return CreateAssignmentSerializer
        else:
            return super().get_serializer_class()

    @swagger_auto_schema(
        operation_description="Add assignment's answer after deadline."
    )
    @action(
        detail=False,
        methods=["post"],
        url_path="add-answer",
        permission_classes=[CanAddAnswer],
    )
    def add_answer(self, request):
        """

        URL: /assignments/{assignment_id}/add_answer/
        Request Body: {"answer_text": "Sample text"} or {"answer_file": <file>}

        """
        try:
            assignment = self.get_object()
            answer_text = request.data.get("answer_text")
            answer_file = request.data.get("answer_file")
            if answer_text:
                assignment.answer_text = answer_text
            if answer_file:
                assignment.answer_file = answer_file
            assignment.save()
            serializer = self.get_serializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Assignment.DoesNotExist:
            return Response(
                {"detail": "The assignment was not found."},
                status=status.HTTP_404_NOT_FOUND,
            )


"""  
class TeacherAssignmentAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request):
        assignments = Assignment.objects.filter(
            class_obj__teacher=request.user
        ).order_by("created_at")
        serializer = AssignmentSerializer(assignments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(
                id=assignment_id, class_obj__teacher=request.user
            )
            serializer = AssignmentSerializer(assignment)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Assignment.DoesNotExist:
            return Response(
                {
                    "error": "The assignment not found or you do not have permission to view it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        serializer = CreateAssignmentSerializer(data=request.data)
        if serializer.is_valid():
            class_obj = serializer.validated_data["class_obj"]
            if class_obj.teacher != request.user:
                return Response(
                    {
                        "error": "You do not have access to create assignments for this class."
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            serializer.save()
            return Response(
                {
                    "message": "Assignment created successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(
                id=assignment_id, class_obj__teacher=request.user
            )
        except Assignment.DoesNotExist:
            return Response(
                {
                    "error": "Assignment not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = CreateAssignmentSerializer(
            assignment, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Assignment updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)




class TeacherAssignmentSolutionAPI(APIView):
    permission_classes = [IsTeacher]

    def patch(self, request, assignment_id):
        try:
            assignment = Assignment.objects.get(
                id=assignment_id, class_obj__teacher=request.user
            )
        except Assignment.DoesNotExist:
            return Response(
                {
                    "error": "Assignment not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = AssignmentSolutionSerializer(
            assignment, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "Assignment's Solution updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

"""


class SolutionViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Solution.objects.all()
    serializer_class = SolutionSerializer

    def get_queryset(self):
        user = self.request.user
        if user.user_type == "teacher":
            assignment_id = self.kwargs.get("assignment_id")
            if assignment_id:
                return Solution.objects.filter(
                    assignment__id=assignment_id, assignment__class_obj__teacher=user
                )
            return Solution.objects.filter(assignment__class_obj__teacher=user)
        elif user.user_type == "student":
            return Solution.objects.filter(student=user)
        return Solution.objects.none()

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update"]:
            permission_classes = [CanSubmitOrUpdateSolution]
        elif self.action == "grade":
            permission_classes = [CanGradeSolution]
        else:
            permission_classes = [CanViewSolution]
        return [permission() for permission in permission_classes]

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_id")
        assignment = Assignment.objects.get(id=assignment_id)
        serializer.save(student=self.request.user, assignment=assignment)

    @swagger_auto_schema(
        operation_description="See all solutions of an assignment by teacher."
    )
    @action(
        detail=False,
        methods=["get"],
        url_path="assignment-solutions",
        url_name="assignment-solutions",
    )
    def assignment_solutions(self, request, pk=None):

        # URL: /solutions/{assignment_id}/assignment-solutions

        try:
            assignment = Assignment.objects.get(id=pk, class_obj__teacher=request.user)
            solutions = Solution.objects.filter(assignment=assignment)
            serializer = self.get_serializer(solutions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Assignment.DoesNotExist:
            return Response(
                {"detail": "The assignment was not found or you do not have access."},
                status=status.HTTP_404_NOT_FOUND,
            )

    @swagger_auto_schema(
        operation_description="Add solution's grade after deadline by teacher."
    )
    @action(detail=True, methods=["post"], permission_classes=[CanGradeSolution])
    def grade(self, request, pk=None):
        """

        URL: /solutions/{solution_id}/grade/
        Request Body: {"grade": 75}

        """
        try:
            solution = self.get_object()
            grade = request.data.get("grade")
            if grade is None:
                return Response(
                    {"detail": "The grade must be provided."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
            solution.grade = grade
            solution.save()
            serializer = self.get_serializer(solution)
            return Response(serializer.data, status=status.HTTP_200_OK)

        except Solution.DoesNotExist:
            return Response({"detail": "The solution not found."}, status=404)


"""  
class TeacherSolutionAPI(APIView):
    permission_classes = [IsTeacher]

    def get(self, request, assignment_id):
        try:
            all_solutions = Solution.objects.filter(
                assignment__id=assignment_id,
                assignment__class_obj__teacher=request.user,
            ).order_by("created_at")
            serializer = TeacherSolutionsSerializer(all_solutions, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Solution.DoesNotExist:
            return Response(
                {
                    "error": "Solution not found or you do not have permission to see it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def get(self, request, solution_id):
        try:
            solution = Solution.objects.get(
                assignment__class_obj__teacher=request.user,
                id=solution_id,
            )
            serializer = TeacherSolutionsSerializer(solution)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Solution.DoesNotExist:
            return Response(
                {
                    "error": "The solution not found or you do not have permission to view it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def patch(self, request, solution_id):
        try:
            solution = Solution.objects.get(
                assignment__class_obj__teacher=request.user,
                id=solution_id,
            )
        except Solution.DoesNotExist:
            return Response(
                {
                    "error": "The solution not found or you do not have permission to update it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )
        serializer = TeacherSolutionsSerializer(
            solution, data=request.data, partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "The grade was assigned successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StudentSolutionAPI(APIView):
    permission_classes = [IsStudent]

    def get(self, request):
        solutions = Solution.objects.filter(student=request.user).order_by("created_at")
        serializer = StudentSolutionSerializer(solutions, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def get(self, request, solution_id):
        try:
            solution = Solution.objects.get(student=request.user, id=solution_id)
            serializer = StudentSolutionSerializer(solution)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Solution.DoesNotExist:
            return Response(
                {
                    "error": "The solution not found or you do not have permission to view it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

    def post(self, request):
        serializer = StudentCreateSolutionSerializer(
            data=request.data, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save(student=request.user)
            return Response(
                {
                    "message": "The solution was submited successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_201_CREATED,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, solution_id):
        try:
            solution = Solution.objects.get(student=request.user, id=solution_id)
        except Solution.DoesNotExist:
            return Response(
                {
                    "error": "The solution not found or you do not have permission to view it."
                },
                status=status.HTTP_404_NOT_FOUND,
            )

        serializer = StudentCreateSolutionSerializer(
            solution, data=request.data, partial=True, context={"request": request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {
                    "message": "The solution was updated successfully.",
                    "data": serializer.data,
                },
                status=status.HTTP_200_OK,
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
