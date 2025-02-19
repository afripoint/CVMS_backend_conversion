from rest_framework.views import APIView
from rest_framework import status
import pandas as pd
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from vins_search.serializers import VinSearchHistorySerializer, VinSerializer
from vins_search.utils import (
    get_vin_status,
    process_csv,
    process_excel,
    process_json,
    process_xml,
)
from django.conf import settings
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.core.files.storage import FileSystemStorage
from rest_framework.generics import GenericAPIView
from rest_framework.exceptions import APIException
from django.db.models import DateField
from rest_framework import generics
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

# from accounts.permissions import HasPermission
# from data_uploads.pagination import AllUploadsPagination
from .models import CustomDutyFile, CustomDutyFileUploads, VinSearchHistory
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class UploadFileAPIView(APIView):
    # permission_classes = [IsAuthenticated, HasPermission]
    # authentication_classes = [JWTAuthentication]

    MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

    @swagger_auto_schema(
        operation_summary="Upload a file and process custom duty payment.",
        operation_description="""
            This endpoint allows you to upload a file (CSV, Excel, JSON, or XML) 
            and updates the custom duty payment based on the content of the file.
            Supported formats: CSV, Excel (.xls/.xlsx), JSON, XML. The file size limit is 5MB.
        """,
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "file": openapi.Schema(
                    type=openapi.TYPE_FILE,
                    description="File to upload (CSV, Excel, JSON, or XML). Max size: 5MB",
                )
            },
        ),
        responses={
            200: openapi.Response(
                description="File processed and saved successfully.",
                examples={
                    "application/json": {
                        "message": "File processed and saved successfully.",
                        "file_url": "http://example.com/uploads/yourfile.csv",
                        "result": {"processed_data": "Details about processed data"},
                    }
                },
            ),
            400: openapi.Response(
                description="Bad request, file validation failed.",
                examples={
                    "application/json": {
                        "error": "File size exceeds the maximum limit of 5MB."
                    },
                    "application/json": {"error": "No file uploaded"},
                    "application/json": {
                        "error": "Invalid file format. Please upload a CSV, Excel, JSON, or XML file."
                    },
                },
            ),
        },
    )
    # Define the maximum allowed file size (in bytes)

    def post(self, request, *args, **kwargs):
        # Check if file is in request
        file = request.FILES.get("file")
        # user = request.user

        # Extract the first_name and last_name
        # first_name = user.first_name
        # last_name = user.last_name

        #  # Check if the user has the 'upload_files' permission
        # if not user.has_permission('upload_files'):
        #     return Response({'detail': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)

        if not file:
            return Response(
                {"error": "No file uploaded"}, status=status.HTTP_400_BAD_REQUEST
            )

        # Check the file size
        if file.size > self.MAX_FILE_SIZE:
            return Response(
                {"error": "File size exceeds the maximum limit of 5MB."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check for duplicate file based on the file name and user
        try:
            file_name = CustomDutyFileUploads.objects.filter(file_name=file.name)
            if file_name.exists():
                return Response(
                    {"message": "This file already exists."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except Exception as e:
            return Response(
                {"error": f"Error checking for duplicate file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Create a FileSystemStorage instance
        storage_location = getattr(settings, "MEDIA_ROOT", "uploads/")
        fs = FileSystemStorage(location=storage_location)
        # Save the file to the uploads directory
        try:
            filename = fs.save(file.name, file)
        except Exception as e:
            return Response(
                {"error": f"Error saving file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Generate the file's URL to be accessed from the frontend
        try:
            file_url = request.build_absolute_uri(settings.MEDIA_URL + filename)

        except Exception as e:
            return Response(
                {"error": f"Error generating file URL: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Process the file based on its extension
        if file.name.endswith(".csv"):
            result = process_csv(file)
            file_type = "csv"
        elif file.name.endswith(".xls", ".xlsx"):
            result = process_excel(file)
            file_type = "excel"
        elif file.name.endswith(".json"):
            file_type = "json"
            result = process_json(file)
        elif file.name.endswith(".xml"):
            result = process_xml(file)
            file_type = "xml"
        else:
            return Response(
                {
                    "message": "Invalid file format. Please upload a CSV, Excel, JSON, or XML file."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        if "error" in result:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)

        try:
            vin_file = CustomDutyFileUploads.objects.create(
                uploaded_by=f"Dennis Akagha",
                file_name=file.name,
                file=filename,
                file_type=file_type,
                processed_status=True,
            )
        except Exception as e:
            return Response(
                {"error": f"Error saving file details to database: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        # Log the upload activity
        # try:
        #     # FileActivityLog.objects.create(
        #     #     uploaded_by=user,
        #     #     file_name=file.name,
        #     #     file_url=file_url,
        #     #     file_type=file_type,
        #     #     file_size=file.size,
        #     #     action_type=FileActivityLog.UPLOAD,
        #     #     ip_address=self.get_client_ip(request),
        #     #     user_agent=request.META.get("HTTP_USER_AGENT", ""),
        #     # )
        # except Exception as e:
        #     # return Response(
        #     #     {"error": f"Error logging file activity: {str(e)}"},
        #     #     status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        #     # )

        # Return the result with the file URL
        return Response(
            {
                "file_url": file_url,
                "result": result,
            },
            status=status.HTTP_200_OK,
        )

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


# class GetAllUploadsAPIView(generics.ListAPIView):
#     # authentication_classes = [JWTAuthentication]
#     # permission_classes = [IsAuthenticated]
#     queryset = CustomDutyFileUploads.objects.all()
#     serializer_class = CustomDutyFileUploadsSerializer
#     pagination_class = AllUploadsPagination

#     @swagger_auto_schema(
#         operation_summary="Retrieve all VIN uploads.",
#         operation_description="""
#             This endpoint retrieves all VINs uploads from the database.
#             It supports pagination for navigating large datasets.
#             The response includes metadata such as total count, next, and previous page links.
#         """,
#         security=[{"Bearer": []}],
#         responses={
#             200: openapi.Response(
#                 description="VIN Uploads fetched successfully.",
#                 examples={
#                     "application/json": {
#                         "message": "All Uploads fetched successfully.",
#                         "metadata": {
#                             "count": 100,
#                             "next": "http://example.com/api/get-all-vins/?page=2",
#                             "previous": None,
#                             "has_next": True,
#                             "has_previous": False,
#                             "current_page": 1,
#                             "total_pages": 10,
#                         },
#                         "data": [
#                             {
#                                 "vin": "1HGCM82633A123456",
#                                 "custom_duty_info": "Duty paid",
#                             },
#                             {
#                                 "vin": "2HGCM82633A654321",
#                                 "custom_duty_info": "Duty unpaid",
#                             },
#                         ],
#                     }
#                 },
#             ),
#             400: openapi.Response(
#                 description="Bad request, error fetching VINs.",
#                 examples={"application/json": {"error": "Error fetching VIN data"}},
#             ),
#         },
#         manual_parameters=[
#             openapi.Parameter(
#                 "start_date",
#                 openapi.IN_QUERY,
#                 description="Filter users from this date (YYYY-MM-DD)",
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#             ),
#             openapi.Parameter(
#                 "end_date",
#                 openapi.IN_QUERY,
#                 description="Filter users up to this date (YYYY-MM-DD)",
#                 type=openapi.TYPE_STRING,
#                 format=openapi.FORMAT_DATE,
#             ),
#             openapi.Parameter(
#                 "request_status",
#                 openapi.IN_QUERY,
#                 description="Filter users by request status (pending, approved, or declined)",
#                 type=openapi.TYPE_STRING,
#             ),
#         ],
#     )
#     def get_queryset(self):
#         queryset = super().get_queryset()

#         # Cast created_at to a date to ignore time when filtering
#         queryset = queryset.annotate(created_at=Cast("uploaded_at", DateField()))

#         # Get the start and end dates from the query parameters
#         start_date = self.request.query_params.get("start_date")
#         end_date = self.request.query_params.get("end_date")


#         # If start_date is provided, filter the queryset from that date onwards
#         if start_date:
#             start_date_parsed = parse_date(start_date)
#             if start_date_parsed:
#                 queryset = queryset.filter(created_at__gte=start_date_parsed)

#         # If end_date is provided, filter the queryset up to that date
#         if end_date:
#             end_date_parsed = parse_date(end_date)
#             if end_date_parsed:
#                 queryset = queryset.filter(created_at__lte=end_date_parsed)

#         return queryset


# # Multi VINSearch
class SingleMultiVinSearchAPIView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                "vins",
                openapi.IN_QUERY,
                description="List of VINs (comma-separated)",
                type=openapi.TYPE_ARRAY,
                items=openapi.Items(type=openapi.TYPE_STRING),
                required=True,
            )
        ]
    )
    def get(self, request):
        vins = request.query_params.getlist("vins")

        if len(vins) > 5:
            return Response(
                {"message": "You cannot perform more than 5 vin checks for this user"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if not vins:
            return Response(
                {"error": "At least one VIN is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []
        for vin in vins:
            api_data = get_vin_status(vin)

            if not api_data or "error" in api_data:
                results.append(
                    {"vin": vin, "error": "Error fetching from external API"}
                )

            try:
                db_vin = CustomDutyFile.objects.get(vin=vin)
                serializer = VinSerializer(db_vin)
                if db_vin.vin == api_data.get("vin"):
                    results.append(serializer.data)
            except CustomDutyFile.DoesNotExist:
                results.append({"vin": vin, "status": "Not found in database"})

        if not results:
            return Response(
                {"error": "No valid VINs found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"message": "Ok", "data": results}, status=status.HTTP_200_OK)


class UploadMultiVinsAPIView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    @swagger_auto_schema(
        operation_summary="Upload an Excel file with VINs for validation",
        operation_description="This endpoint allows users to upload an Excel file (.xlsx) containing a list of VINs. "
        "The VINs are validated against an external API and compared with the database records.",
        manual_parameters=[
            openapi.Parameter(
                name="file",
                in_=openapi.IN_FORM,
                type=openapi.TYPE_FILE,
                description="Excel file (.xlsx) containing a 'vin' column",
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="VIN validation results",
                examples={
                    "application/json": {
                        "message": "Ok",
                        "data": [
                            {
                                "vin": "1HGCM82633A123456",
                                "owner": "John Doe",
                                "registered": True,
                            },
                            {
                                "vin": "JH4KA8260MC123456",
                                "status": "Not found in database",
                            },
                        ],
                    }
                },
            ),
            400: openapi.Response(
                description="Bad Request - File missing or invalid format"
            ),
            404: openapi.Response(description="No valid VINs found"),
            500: openapi.Response(description="Server Error"),
        },
    )
    def post(self, request, *args, **kwargs):
        # Check if a file is uploaded
        file = request.FILES.get("file")

        if not file:
            return Response(
                {"error": "No file uploaded"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if file.name.endswith(".xlsx"):
            df = pd.read_excel(file)

        if "vin" not in df.columns:
            return Response(
                {"error": "The file must contain a 'vin' column."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        vins = df["vin"].dropna().astype(str).tolist()

        if not vins:
            return Response(
                {"error": "No VINs found in the file"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(vins) > 20:  # Limit for better performance
            return Response(
                {"error": "Cannot validate more than 20 VINs at once"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        results = []

        for vin in vins:
            # Validate with External API
            api_data = get_vin_status(vin)

            if not api_data or "error" in api_data:
                results.append(
                    {"vin": vin, "error": "Error fetching from external API"}
                )

            # Check in Database
            try:
                db_vin = CustomDutyFile.objects.get(vin=vin)
                serializer = VinSerializer(db_vin)
                if db_vin.vin == api_data.get("vin"):
                    results.append(serializer.data)
            except CustomDutyFile.DoesNotExist:
                results.append({"vin": vin, "status": "Not found in database"})

        if not results:
            return Response(
                {"error": "No valid VINs found"}, status=status.HTTP_404_NOT_FOUND
            )

        return Response({"message": "Ok", "data": results}, status=status.HTTP_200_OK)


class VINSearchHistoryListAPIView(APIView):
    def get(self, request):
        user = request.user
        histories = VinSearchHistory.objects.filter(user=user)
        serializer = VinSearchHistorySerializer(histories, many=True)
        response = {
            "Search_histories": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)


# VIN Search History Detail
class VINSearchHistoryDetailAPIView(APIView):
    def get(self, request, vin):
        user = request.user
        history = get_object_or_404(VinSearchHistory, vin=vin, user=user)
        serializer = VinSearchHistorySerializer(history)
        response = {
            "data": serializer.data,
        }
        return Response(data=response, status=status.HTTP_200_OK)
