
export type Vacancy = {
  id: number;
  job_title_nm: string; // [translate:"Название вакансии"]
  job_category: number; // id of JobCategory, [translate:"Категория работы"]
  area: number; // id of Area, [translate:"Регион"]
  lower_bound_salary_amt?: number | null; // [translate:"Минимальная зарплата"]
  upper_bound_salary_amt?: number | null; // [translate:"Максимальная зарплата"]
  salary_currency: number; // id of Currency, [translate:"Валюта"]
  employer: number; // id of Employer, [translate:"Работодатель"]
  employment_type: number; // id of EmploymentType, [translate:"Тип занятости"]
  experience_type: number; // id of ExperienceType, [translate:"Требуемый опыт"]
  vacancy_publish_dttm: string; // ISO date string, [translate:"Дата публикации"]
  vacancy_archive_flg: boolean; // [translate:"Архивная"]
};
