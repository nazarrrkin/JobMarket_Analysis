from rest_framework import status
from rest_framework.viewsets import ViewSet
from rest_framework.decorators import action
from rest_framework.response import Response
from core.utilities.csv_processor import DataImportService
from .models import (
    Area, JobCategory, Employer, Vacancy, 
    EmploymentType, ExperienceType, Currency
)
import logging

logger = logging.getLogger(__name__)

class ParserDataView(ViewSet):
    
    @action(detail=False, methods=['post'])
    def post(self, request):
        try:
            # Получаем файлы из запроса
            area_file = request.FILES.get('area')
            job_category_file = request.FILES.get('job_category')
            employees_file = request.FILES.get('employees')
            vacancy_file = request.FILES.get('vacancy')
            
            if not all([area_file, job_category_file, employees_file, vacancy_file]):
                return Response(
                    {'error': 'Все 4 файла обязательны для загрузки'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Подготавливаем файлы и модели
            files = {
                'area': area_file,
                'job_category': job_category_file,
                'employees': employees_file,
                'vacancy': vacancy_file
            }
            
            models = {
                'Area': Area,
                'JobCategory': JobCategory,
                'Employer': Employer,
                'Vacancy': Vacancy,
                'EmploymentType': EmploymentType,
                'ExperienceType': ExperienceType,
                'Currency': Currency
            }
            
            # Импортируем данные используя сервис
            stats = DataImportService.import_all_data(files, models)
            
            logger.info(f"Статистика импорта: {stats}")
            
            return Response({
                'message': 'Файлы успешно обработаны',
                'stats': stats
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            logger.error(f"Ошибка при обработке файлов: {str(e)}")
            return Response(
                {'error': f'Ошибка при обработке файлов: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    def get_vacancy_list(self, request):
        pass