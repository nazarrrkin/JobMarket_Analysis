\encoding UTF8

DROP TABLE IF EXISTS hh_raw_vacancies;

CREATE TABLE hh_vacancies_raw(
    vacancy_id TEXT,
    vacancy_name TEXT,
    professional_roles_id TEXT,
    professional_roles_name TEXT,
    area_id TEXT,
    area_name TEXT,
    salary_from TEXT,
    salary_to TEXT,
    currency TEXT,
    gross TEXT,
    requirement TEXT,
    employer_id TEXT,
    employer_name TEXT,
    schedule TEXT,
    experience TEXT,
    employment_form TEXT,
    work_format TEXT,
    vacancy_publish_date TIMESTAMP,
    is_archived TEXT
);

\copy hh_vacancies_raw from 'hh_raw_vacancies.csv' delimiter ',' csv header;

drop table if exists vacancy;
create table vacancy as
select distinct on (vacancy_id)
       vacancy_id
     , vacancy_name as job_title_nm
	 , cast(case when professional_roles_id is not null and coalesce(professional_roles_name, 'None') <> 'None'
	        then professional_roles_id
			else null
	   end as integer) as job_category_id
	 , cast(case when coalesce(area_id, 'None') <> 'None' and coalesce(area_name, 'None') <> 'None'
	        then area_id
			else null
	   end as integer) as area_id
	 , case when salary_from = 'None'
	        then null
			else salary_from
	   end as lower_bound_salary_amt
	 , case when salary_to = 'None'
	        then null
			else salary_to
	   end as upper_bound_salary_amt
	 , case when currency = 'None'
 	        then null
			else currency
	   end as salary_currency_code
	 , cast(case when employer_id is not null and coalesce(employer_name, 'None') <> 'None'
	        then employer_id
			else null
		end as integer) as employer_id
	 , case when schedule = 'None' then null
			when replace(lower(schedule), ' ', '') like 'flex%' then 'Гибкий график'
			when replace(lower(schedule), ' ', '') like 'flyinflyout%' then 'Вахта'
			when replace(lower(schedule), ' ', '') like 'fullday%' then 'Полный рабочий день'
			when replace(lower(schedule), ' ', '') like 'remote%' then 'Удаленная работа'
			when replace(lower(schedule), ' ', '') like 'shift%' then 'Смена'
			else schedule
	   end as employment_type_desc
	 , case when experience = 'None' then null
			when replace(lower(experience), ' ', '') like 'between1and3%' then 'От 1 года до 3-x лет'
			when replace(lower(experience), ' ', '') like 'between3and6%' then 'От 3-х до 6-ти лет'
			when replace(lower(experience), ' ', '') like 'morethan6%' then 'Более 6-ти лет'
			when replace(lower(experience), ' ', '') like 'noexperience%' then 'Без опыта'
			else experience
	   end as experience_type_desc
	 , vacancy_publish_date as vacancy_publish_dttm
	 , cast(cast(is_archived as integer) as smallint) as vacancy_archive_flg
from hh_vacancies_raw
where 1 = 1
and vacancy_id is not null
and coalesce(vacancy_name, 'None') <> 'None'
order by vacancy_id, is_archived, vacancy_publish_date desc, vacancy_name
;

drop table if exists job_category;
create table job_category as
select distinct on (professional_roles_id)
       professional_roles_id as job_category_id
	 , professional_roles_name as job_category_nm
from hh_vacancies_raw
where 1 = 1
and professional_roles_id is not null
and coalesce(professional_roles_name, 'None') <> 'None'
order by professional_roles_id, professional_roles_name
;

drop table if exists area;
create table area as
select distinct on (area_id)
       area_id
	 , area_name as area_nm
from hh_vacancies_raw
where 1 = 1
and coalesce(area_id, 'None') is not null
and coalesce(area_name, 'None') <> 'None'
order by area_id, area_name
;

drop table if exists employer;
create table employer as
select distinct on (employer_id)
       employer_id
	 , employer_name as employer_nm
from hh_vacancies_raw
where 1 = 1
and employer_id is not null
and coalesce(employer_name, 'None') <> 'None'
order by employer_id, employer_name
;

\copy vacancy to 'vacancy.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');
\copy area to 'area.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');
\copy job_category to 'job_category.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');
\copy employer to 'employer.csv' WITH (FORMAT CSV, HEADER, DELIMITER ',');
