
import csv
import io
import  chardet
import logging
from django.db import transaction
from django.utils import timezone

logger = logging.getLogger(__name__)

class CSVProcessor:
    """Утилита для обработки CSV файлов"""
    
    @staticmethod
    def detect_encoding(file):
        """Определяет кодировку файла"""
        raw_data = file.read()
        file.seek(0)  # Возвращаем указатель в начало файла
        
        result = chardet.detect(raw_data)
        encoding = result.get('encoding', 'utf-8')
        confidence = result.get('confidence', 0)
        
        logger.info(f"Определена кодировка: {encoding} с уверенностью: {confidence}")
        
        # Если уверенность низкая, пробуем windows-1251 для русских текстов
        if confidence < 0.7:
            encoding = 'windows-1251'
            
        return encoding, raw_data
    
    @staticmethod
    def decode_file_content(file):
        """Декодирует содержимое файла с автоматическим определением кодировки"""
        encoding, raw_data = CSVProcessor.detect_encoding(file)
        
        try:
            return raw_data.decode(encoding)
        except UnicodeDecodeError:
            # Если не получилось, пробуем другие кодировки
            for enc in ['windows-1251', 'cp1251', 'iso-8859-1', 'utf-8']:
                try:
                    decoded_content = raw_data.decode(enc)
                    return decoded_content
                except UnicodeDecodeError:
                    continue
            # Если все кодировки не подошли, используем replace для замены нечитаемых символов
            return raw_data.decode('utf-8', errors='replace')
    
    @staticmethod
    def process_area_file(file, Area):
        """Обработка CSV файла с областями"""
        decoded_content = CSVProcessor.decode_file_content(file)
        io_string = io.StringIO(decoded_content)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            # Создаем или обновляем область
            area, created = Area.objects.update_or_create(
                id=row['area_id'],
                defaults={'name': row['area_nm']}
            )
            if created:
                created_count += 1
                
        return created_count
    
    @staticmethod
    def process_job_category_file(file, JobCategory):
        """Обработка CSV файла с категориями работ"""
        decoded_content = CSVProcessor.decode_file_content(file)
        io_string = io.StringIO(decoded_content)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            # Создаем или обновляем категорию работы
            category, created = JobCategory.objects.update_or_create(
                id=row['job_category_id'],
                defaults={'name': row['job_category_nm']}
            )
            if created:
                created_count += 1
                
        return created_count
    
    @staticmethod
    def process_employees_file(file, Employer):
        """Обработка CSV файла с работодателями"""
        decoded_content = CSVProcessor.decode_file_content(file)
        io_string = io.StringIO(decoded_content)
        reader = csv.DictReader(io_string)
        
        created_count = 0
        for row in reader:
            # Предполагаем, что в файле есть employer_id и employer_nm
            # Если структура другая, нужно адаптировать
            employer_id = row.get('employer_id') or row.get('id')
            employer_name = row.get('employer_nm') or row.get('name')
            
            if employer_id and employer_name:
                employer, created = Employer.objects.update_or_create(
                    id=employer_id,
                    defaults={'name': employer_name}
                )
                if created:
                    created_count += 1
                
        return created_count
    
    @staticmethod
    def process_vacancy_file(file, models):
        """Обработка CSV файла с вакансиями"""
        decoded_content = CSVProcessor.decode_file_content(file)
        io_string = io.StringIO(decoded_content)
        reader = csv.DictReader(io_string)
        
        # Извлекаем модели из словаря
        Vacancy = models['Vacancy']
        JobCategory = models['JobCategory']
        Area = models['Area']
        Employer = models['Employer']
        EmploymentType = models['EmploymentType']
        ExperienceType = models['ExperienceType']
        Currency = models['Currency']
        
        created_count = 0
        
        for row in reader:
            try:
                # Получаем связанные объекты
                job_category = JobCategory.objects.get(id=row['job_category_id'])
                area = Area.objects.get(id=row['area_id'])
                employer = Employer.objects.get(id=row['employer_id'])
                
                # Получаем или создаем типы занятости и опыта по умолчанию
                employment_type, _ = EmploymentType.objects.get_or_create(
                    name=row.get('employment_type_name', 'Полная занятость')
                )
                
                experience_type, _ = ExperienceType.objects.get_or_create(
                    name=row.get('experience_type_name', 'От 1 года до 3 лет')
                )
                
                # Получаем или создаем валюту (по умолчанию RUB)
                currency, _ = Currency.objects.get_or_create(
                    code=row.get('salary_currency_code', 'RUB'),
                    defaults={'name': 'Российский рубль'}
                )
                
                # Преобразуем булево значение
                archive_flag = row.get('vacancy_archive_flg', 'false').lower() in ('true', '1', 'yes')
                
                # Обрабатываем зарплату (может быть пустой строкой)
                lower_salary = row.get('lower_bound_salary_amt')
                upper_salary = row.get('upper_bound_salary_amt')
                
                lower_salary = float(lower_salary) if lower_salary and lower_salary.strip() else None
                upper_salary = float(upper_salary) if upper_salary and upper_salary.strip() else None
                
                # Создаем или обновляем вакансию
                vacancy, created = Vacancy.objects.update_or_create(
                    vacancy_id=row['vacancy_id'],
                    defaults={
                        'job_title_nm': row['job_title_nm'],
                        'job_category': job_category,
                        'area': area,
                        'lower_bound_salary_amt': lower_salary,
                        'upper_bound_salary_amt': upper_salary,
                        'salary_currency': currency,
                        'employer': employer,
                        'employment_type': employment_type,
                        'experience_type': experience_type,
                        'vacancy_archive_flg': archive_flag,
                    }
                )
                
                if created:
                    created_count += 1
                    
            except KeyError as e:
                logger.warning(f"Отсутствует обязательное поле в строке вакансии: {e}")
                continue
            except (JobCategory.DoesNotExist, Area.DoesNotExist, Employer.DoesNotExist) as e:
                logger.warning(f"Связанный объект не найден: {e}")
                continue
            except Exception as e:
                logger.error(f"Ошибка при обработке вакансии {row.get('vacancy_id', 'unknown')}: {e}")
                continue
                
        return created_count


class DataImportService:
    """Сервис для импорта данных из CSV файлов"""
    
    @staticmethod
    @transaction.atomic
    def import_all_data(files, models):
        """
        Импортирует все данные из CSV файлов
        
        Args:
            files: словарь с файлами {'area': file, 'job_category': file, ...}
            models: словарь с моделями Django
            
        Returns:
            dict: статистика по обработанным данным
        """
        stats = {}
        
        # Обрабатываем области
        if files.get('area'):
            stats['areas_created'] = CSVProcessor.process_area_file(
                files['area'], models['Area']
            )
        
        # Обрабатываем категории работ
        if files.get('job_category'):
            stats['categories_created'] = CSVProcessor.process_job_category_file(
                files['job_category'], models['JobCategory']
            )
        
        # Обрабатываем работодателей
        if files.get('employees'):
            stats['employers_created'] = CSVProcessor.process_employees_file(
                files['employees'], models['Employer']
            )
        
        # Обрабатываем вакансии
        if files.get('vacancy'):
            stats['vacancies_created'] = CSVProcessor.process_vacancy_file(
                files['vacancy'], models
            )
        
        return stats