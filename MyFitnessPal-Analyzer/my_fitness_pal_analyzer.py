from src.utils.common import  read_csv
from src.utils.settings import PATH_NUTRITION_SUMMARY_CSV, PATH_MEASUREMENT_SUMMARY_CSV, PATH_EXERCISE_SUMMARY_CSV
from src.nutrition import NutritionData, NutritionDay, HealthyDay, HealthyWeek
from csv import DictReader
from typing import Dict, Any, List
from datetime import datetime, date
from prettytable import PrettyTable

def read_nutrition_data(csv_data: DictReader) ->  Dict[str, Any]:
    line_count = 0
    nutrition_datas = {}
    for row in csv_data:
        date = row['Date']
        meal = row['Meal']
        calories = float(row['Calories'])
        fat = float(row['Fat (g)'])
        saturated_fat = float(row['Saturated Fat'])
        fiber = float(row['Fiber'])
        sugar = float(row['Sugar'])
        protein = float(row['Protein (g)'])
        carbohydrates = float(row['Carbohydrates (g)'])
        nutrition_data = NutritionData(fat, saturated_fat, fiber, protein, carbohydrates, sugar,calories,date)
        nutrition_data_day = nutrition_datas.setdefault(date,{})
        nutrition_data_day[meal] = nutrition_data
    return nutrition_datas

def read_nutrition_days(csv_data: DictReader) -> Dict[str, NutritionDay]:
    nutrition_datas = read_nutrition_data(csv_data)
    nutrition_days = {}
    for date in nutrition_datas:
        breakfast = nutrition_datas[date].get('Breakfast', NutritionData(date=date))
        lunch = nutrition_datas[date].get('Lunch', NutritionData(date=date))
        dinner = nutrition_datas[date].get('Dinner', NutritionData(date=date))
        snack = nutrition_datas[date].get('Snacks', NutritionData(date=date))
        nutrition_day = NutritionDay(breakfast, lunch, dinner, snack, date)
        assert date not in nutrition_days, f"Duplicate nutrition Date, date {date} is alreadu in the set"
        nutrition_days[date] = nutrition_day
    return nutrition_days

def read_measurement(csv_data: DictReader) -> Dict[str, float]:
    measurements = {}
    for row in csv_data:
        date = row['Date']
        weight = float(row['Weight'])
        assert date not in measurements, f"Duplicate weight date, date {date} is alreadu in the set"
        measurements[date] = weight
    return measurements

def read_exercise(csv_data: DictReader) -> Dict[str, int]:
    exercise_minutes = {}
    for row in csv_data:
        date = row['Date']
        exercise_minute = int(row['Exercise Minutes'])
        assert exercise_minute >= 0, f"Exercise minute must be equal or greater than 0, got {exercise_minute}"
        current_minutes = exercise_minutes.setdefault(date,0)
        exercise_minutes[date] = current_minutes + int(exercise_minute)
    return exercise_minutes

def get_healthy_days(nutrition_days: Dict[str, NutritionDay], measurements: Dict[str, float], exercises :
                     Dict[str,int]) -> Dict[str, HealthyDay]:
    healthy_days = {}
    #merging dates across categories
    all_dates = set(exercises) | set(nutrition_days) | set(measurements)
    for date in all_dates:
        year = date.split('-')[0]
        month = date.split('-')[1]
        day = date.split('-')[2]
        nutrition_day = nutrition_days.get(date, NutritionDay(
                                                                breakfastNutritionData=NutritionData(date=date),
                                                                lunchNutritionData=NutritionData(date=date),
                                                                dinnerNutritionData=NutritionData(date=date),
                                                                snacksNutritionData=NutritionData(date=date),
                                                                date=date
                                                              )
                                           )
        measurement = measurements.get(date, 0.0)
        exercise=  exercises.get(date, 0)
        healthy_day = HealthyDay(day, month, year, nutrition_day, exercise, measurement)
        healthy_days[date] = healthy_day
    return healthy_days

def get_healthy_weeks(healthy_days: Dict[date, HealthyDay]) -> Dict[str, HealthyWeek]:
    healthy_weeks_output = {} # key: year-week_number, value: HealthyWeek
    healthy_weeks_wip = {} # key: year-week_number, value: List[HealthyDay]
    for date in healthy_days:
        healthy_day = healthy_days.get(date)
        year, month, day =  healthy_day.get_year_month_day()
        #get week number
        date_str = f"{year}-{month}-{day}"
        date = datetime.strptime(date_str, '%Y-%m-%d')
        week_num = date.isocalendar()[1]
        #add healthy_days to the list of healthy_days for the specific week
        id = f"{year}-{week_num}"
        week_wip = healthy_weeks_wip.setdefault(id,[])
        week_wip.append(healthy_day)
    for healthy_week_key in healthy_weeks_wip:
        year = int(healthy_week_key.split('-')[0])
        week_num = healthy_week_key.split('-')[1]
        first_day_of_the_week = int(date.fromisocalendar(int(year),int(week_num),1).day)
        month = int(date.fromisocalendar(int(year),int(week_num),1).month)
        date = datetime(year,month,first_day_of_the_week)
        healthy_weeks_output[date] = HealthyWeek(year, week_num, healthy_weeks_wip[healthy_week_key])
    return healthy_weeks_output





if __name__ == "__main__":
    #read data from csv
    nutrition_data_file = read_csv(PATH_NUTRITION_SUMMARY_CSV)
    nutrition_days_read_from_file = read_nutrition_days(nutrition_data_file)
    measurement_data_file = read_csv(PATH_MEASUREMENT_SUMMARY_CSV)
    measurements_read_from_file = read_measurement(measurement_data_file)
    exercise_data_file = read_csv(PATH_EXERCISE_SUMMARY_CSV)
    exercise_read_from_file = read_exercise(exercise_data_file)
    healthy_days = get_healthy_days(nutrition_days_read_from_file, measurements_read_from_file, exercise_read_from_file)
    healthy_weeks = get_healthy_weeks(healthy_days)

    #Nice printing
    healthy_weeks_list = list(healthy_weeks.keys())
    healthy_weeks_list.sort(reverse=False)

    header = ["Week ID", "Month", "Days", "Healthy Days", "Days with Nutr.", "Avg Fat", "Fat by Kg", "Avg Sat.F",
              "Avg Fiber","Avg Prot", "Prot by Kg", "Avg Carbs", "Avg Sug", "Tot Exer.", "Avg Exer", "Avg Weight"]
    pretty_table = PrettyTable(header)
    for sorted_week in healthy_weeks_list:
        healthy_week = healthy_weeks[sorted_week]
        week_id = healthy_week.id
        month = healthy_week.month
        days = healthy_week.days_range
        healthy_days = healthy_week.healthy_days_num
        healthy_days_w_nutr = healthy_week.healthy_days_with_nutrition_number
        avg_fat = healthy_week.avarage_fat
        fat_by_kg = healthy_week.fat_by_kg
        avg_sat_fat = healthy_week.avarage_saturated_fat
        avg_fiber = healthy_week.avarage_fiber
        avg_prot = healthy_week.avarage_protein
        prot_by_kg = healthy_week.protein_by_kg
        avg_carbs = healthy_week.avarage_carbohydrate
        avg_sugar = healthy_week.avarage_sugar
        total_exer = healthy_week.total_exercise
        avg_exer = healthy_week.avarage_exercise
        avg_weight = healthy_week.avarage_weight
        pretty_table.add_row([week_id, month, days, healthy_days,healthy_days_w_nutr,avg_fat, fat_by_kg, avg_sat_fat,
                              avg_fiber,avg_prot,prot_by_kg, avg_carbs, avg_sugar, total_exer, avg_exer, avg_weight])
    print(pretty_table)
