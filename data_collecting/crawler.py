import requests
import time
import csv
import os

class hh_crawler():
    def __init__(self):
        self.headers = {}
        self.area = ['Москва','Санкт-Петербург', 'Новосибирск', 'Екатеринбург', 'Нижний Новгород',  'Челябинск', 'Самара', 'Омск', 'Воронеж', 'Сочи']
        self.vacancies = []
        self.requests_per_second = 2
        self.total_requests = 100000
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'ru-RU,ru;q=0.9,en-US;q=0.8,en;q=0.7',
        })


    def get_areas_id(self):
        regions = {}
        url = 'https://api.hh.ru/areas/113'
        data = self.session.get(url).json()
        for city in data['areas']:
            if not city['areas']:
                regions[city['id']] = city['name']
            for town in city['areas']:
                if not town['areas']:
                    regions[town['id']] = town['name']
        return {city_id:name for city_id, name in regions.items() if name in self.area}


    def get_professional_roles(self):
        professional_roles = {}
        url = 'https://api.hh.ru/professional_roles'
        data = self.session.get(url).json()
        for categories in data['categories']:
            for roles in categories['roles']:
                professional_roles[roles['id']] = roles['name']
        return professional_roles


    def vacancy_info(self, region_id, profession, page_num):
        url = 'https://api.hh.ru/vacancies'
        params = {'order_by': 'publication_time',
                  'per_page': 100,
                  'page': page_num,
                  'area': region_id,
                  'text': profession}
        data = self.session.get(url, params=params).json()
        try:
            for vacancy in data['items']:
                vacancy_info = {'vacancy_id': vacancy['id'],
                                'vacancy_name': vacancy['name'],
                                'professional_roles_id': ','.join(item['id'] for item in vacancy['professional_roles']) if vacancy['professional_roles'] else 'None',
                                'professional_roles_name': ','.join(item['name'] for item in vacancy['professional_roles']) if vacancy['professional_roles'] else 'None',
                                'area_id': vacancy['area']['id'] if vacancy['salary'] else 'None',
                                'area_name': vacancy['area']['name'] if vacancy['salary'] else 'None',
                                'salary_from': vacancy['salary']['from'] if vacancy['salary'] else 'None',
                                'salary_to': vacancy['salary']['to'] if vacancy['salary'] else 'None',
                                'currency': vacancy['salary']['currency'] if vacancy['salary'] else 'None',
                                'gross': vacancy['salary']['gross'] if vacancy['salary'] else 'None',
                                'requirement':vacancy['snippet']['requirement'] if vacancy['snippet'] else 'None',
                                'employer_id': vacancy['employer'].get('id') if vacancy['employer'] else 'None',
                                'employer_name': vacancy['employer'].get('name') if vacancy['employer'] else 'None',
                                'schedule': vacancy['schedule']['id'],
                                'experience': vacancy['experience']['id'],
                                'employment_form': vacancy['employment_form']['id'],
                                'work_format': ','.join(item['id'] for item in vacancy['work_format']) if vacancy['work_format'] else 'None',
                                'vacancy_publish_date': vacancy['published_at'],
                                'is_archived': vacancy['archived']
                }
                self.vacancies.append(vacancy_info)
        except Exception as e:
            print(data)


    def get_vacancies(self):
        areas_id = self.get_areas_id()
        professional_roles = self.get_professional_roles()
        for region in areas_id.keys():
            print(f'\nCollecting data for region: {region}')
            for profession in professional_roles.keys():
                print(f'Processing profession {profession} for city {region}')
                for page_num in range(0, 20):
                    time.sleep(1/self.requests_per_second)
                    self.vacancy_info(region, profession, page_num)
                self.save_to_csv()
                self.vacancies = []


    def save_to_csv(self):
        file_exists = os.path.exists('hh_raw_vacancies.csv')
        with open('hh_raw_vacancies.csv', 'a', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=self.vacancies[0].keys())
            if not file_exists :
                writer.writeheader()
            writer.writerows(self.vacancies)

if __name__ == '__main__':
    crawler = hh_crawler()
    crawler.get_vacancies()
    print(f'Data was collected succesfully!')
