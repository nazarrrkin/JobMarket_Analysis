from django.db import models
from django.utils import timezone
# Create your models here.

class Employer(models.Model):
    name = models.CharField(max_length=300)


class Area(models.Model):
    name = models.CharField(max_length=300)

class JobCategory(models.Model):
    name = models.CharField(max_length=300)


class EmploymentType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name


# Для уровней опыта
class ExperienceType(models.Model):
    name = models.CharField(max_length=100)
    
    def __str__(self):
        return self.name

# Для валют
class Currency(models.Model):
    code = models.CharField(max_length=3)
    name = models.CharField(max_length=50)
    
    def __str__(self):
        return self.code

class Vacancy(models.Model):
    vacancy_id = models.AutoField(primary_key=True)
    job_title_nm = models.CharField(max_length=300, verbose_name="Название вакансии")
    job_category = models.ForeignKey(JobCategory, on_delete=models.CASCADE, verbose_name="Категория работы")
    area = models.ForeignKey(Area, on_delete=models.CASCADE, verbose_name="Регион")
    lower_bound_salary_amt = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Минимальная зарплата")
    upper_bound_salary_amt = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, verbose_name="Максимальная зарплата")
    salary_currency = models.ForeignKey(Currency, on_delete=models.PROTECT, default=1, verbose_name="Валюта")
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, verbose_name="Работодатель")
    employment_type = models.ForeignKey(EmploymentType, on_delete=models.PROTECT, verbose_name="Тип занятости")
    experience_type = models.ForeignKey(ExperienceType, on_delete=models.PROTECT, verbose_name="Требуемый опыт")
    vacancy_publish_dttm = models.DateTimeField(default=timezone.now, verbose_name="Дата публикации")  # Изменено здесь
    vacancy_archive_flg = models.BooleanField(default=False, verbose_name="Архивная")
    
    class Meta:
        verbose_name = "Вакансия"
        verbose_name_plural = "Вакансии"
        db_table = 'vacancy'
        ordering = ['-vacancy_publish_dttm']
    
    def __str__(self):
        return self.job_title_nm
    
    @property
    def salary_range(self):
        """Возвращает форматированный диапазон зарплат"""
        if self.lower_bound_salary_amt and self.upper_bound_salary_amt:
            return f"{self.lower_bound_salary_amt} - {self.upper_bound_salary_amt} {self.salary_currency.code}"
        elif self.lower_bound_salary_amt:
            return f"от {self.lower_bound_salary_amt} {self.salary_currency.code}"
        elif self.upper_bound_salary_amt:
            return f"до {self.upper_bound_salary_amt} {self.salary_currency.code}"
        return "Не указана"