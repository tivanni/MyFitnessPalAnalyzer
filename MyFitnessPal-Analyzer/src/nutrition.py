
from typing import Optional, List
from abc import ABC
from datetime import datetime, date

class NutritionData:
    def __init__(self, fat: Optional[float] = 0.0 , saturated_fat: Optional[float] = 0.0, fiber: Optional[float] = 0.0,
                 protein: Optional[float] = 0.0, carbohydrate: Optional[float] = 0.0, sugar: Optional[float] = 0.0,
                 calories: Optional[float] = 0.0 , date: Optional[str] = None):
        assert saturated_fat <= fat, (f"Saturated fat should be less than or equal to fat. "
                                      f"Values: saturated_fat {saturated_fat}, fat {fat}")

        assert (isinstance(fat, float) and isinstance(saturated_fat,float) and isinstance(fiber, float) and
                isinstance(protein, float) and isinstance(carbohydrate,float) and isinstance(sugar, float)), \
            (f"one of the input is not a float: {fat} {saturated_fat} {fiber} {protein} {carbohydrate}"
             f"{sugar} {calories} {date} ")
        self.fat = round(fat,1)
        self.saturated_fat = round(saturated_fat,1)
        self.fiber = round(fiber,1)
        self.protein = round(protein,1)
        self.carbohydrate = round(carbohydrate,1)
        self.sugar = round(sugar,1)
        self.calories = calories
        #variable indicating if the NutritionData was actually consumed or not
        self.consumed = False
        #consider the meal as consumed if any of the macro is > 0
        if fat > 0 or protein > 0 or carbohydrate > 0:
            self.consumed = True
        #assert date
        self.date = date
        format = "%Y-%m-%d"
        try:
            res = bool(datetime.strptime(self.date, format))
        except ValueError:
            print(f"Invalid date format, got {self.date}" )
            exit(0)
    def __str__(self):
        return(
            f"Nutrition data | fat: {self.fat} | saturated: {self.saturated_fat} | fiber: {self.fiber} | "
            f"protein: {self.protein} | carbohydrate: {self.carbohydrate} | sugar: {self.sugar} | "
            f"consumed: {self.consumed}, date: {self.date}"
        )

class NutritionDay:
    def __init__(self ,breakfastNutritionData: NutritionData,
                 lunchNutritionData: NutritionData,
                 dinnerNutritionData: NutritionData, snacksNutritionData: NutritionData, date: str):
        self.breakfastNutritionData = breakfastNutritionData
        self.lunchNutritionData = lunchNutritionData
        self.dinnerNutritionData = dinnerNutritionData
        self.snacksNutritionData = snacksNutritionData

        # assert date
        self.date = date
        format = "%Y-%m-%d"
        try:
            res = bool(datetime.strptime(self.date, format))
        except ValueError:
            print(f"Invalid date format, got {self.date}")
            exit(0)
        #assert NutritionData are for the right day
        assert (breakfastNutritionData.date == self.date and lunchNutritionData.date == self.date and
                dinnerNutritionData.date ==self.date and snacksNutritionData.date ==self.date), (f"invalid date for "
                                                                                                 f"nutrition data in"
                                                                                                 f"day {self.date}")
        #consider a nutrition day completed if at least two of the major meals are completed
        self.consumed = False
        if ((self.breakfastNutritionData.consumed and self.lunchNutritionData.consumed) or
            (self.breakfastNutritionData.consumed and self.dinnerNutritionData.consumed) or
            (self.lunchNutritionData.consumed and self.dinnerNutritionData.consumed)):
            self.consumed = True




        #compute total
        self.total_fat = round((self.breakfastNutritionData.fat + self.lunchNutritionData.fat + self.dinnerNutritionData.fat +
                          self.snacksNutritionData.fat),1)
        self.total_saturated_fat = round((self.breakfastNutritionData.saturated_fat + self.lunchNutritionData.saturated_fat +
                                    self.dinnerNutritionData.saturated_fat + self.snacksNutritionData.saturated_fat),1)
        self.total_fiber = round((self.breakfastNutritionData.fiber + self.lunchNutritionData.fiber +
                            self.dinnerNutritionData.fiber + self.snacksNutritionData.fiber),1)
        self.total_protein = round((self.breakfastNutritionData.protein + self.lunchNutritionData.protein +
                              self.dinnerNutritionData.protein + self.snacksNutritionData.protein),1)
        self.total_carbohydrate = round((self.breakfastNutritionData.carbohydrate + self.lunchNutritionData.carbohydrate +
                                   self.dinnerNutritionData.carbohydrate + self.snacksNutritionData.carbohydrate),1)
        self.total_sugar = round((self.breakfastNutritionData.sugar + self.lunchNutritionData.sugar +
                            self.dinnerNutritionData.sugar + self.snacksNutritionData.sugar),1)
    def __str__(self):
        return(
            f'breakfast: {self.breakfastNutritionData}| lunch: {self.lunchNutritionData} | '
            f'dinner: {self.dinnerNutritionData}, snack: {self.snacksNutritionData}, date: {self.date}\n'
        )

class HealthyDay:
    def __init__(self, day: str, month: str, year: str, nutrition_day: NutritionDay = None,
                 total_exercise_minutes: int = 0, weight: float=0.0 ):
        self.id = int(f"{year}{month}{day}")
        self.human_id = f"{year}-{month}-{day}"
        # assert date
        format = "%Y-%m-%d"
        try:
            res = bool(datetime.strptime(self.human_id, format))
        except ValueError:
            print(f"Invalid date format, got {year}{month}{day}" )
            return 0

        self.year = year
        self.month = month
        self.day = day

        #populate nutritional value
        self.nutrition_day = nutrition_day
        assert total_exercise_minutes >= 0, f"Exercise minutes must be positive integer, got {total_exercise_minutes}"
        self.exercise_minutes = total_exercise_minutes
        assert weight >=0, f"Weight must be positive integer, got {weight}"
        self.weight = weight

    def get_year_month_day(self):
        return self.year, self.month, self.day

    def __repr__(self):
        return(
            f"day: {self.human_id} | NutritionDay: {self.nutrition_day.consumed} | Exercise: {self.exercise_minutes} |"
            f"weight: {self.weight}\n"
        )

class HealthyDayGroup(ABC):
    def __init__(self, healthy_days:List[HealthyDay]):
        assert len(healthy_days) > 0, f"Healthy days must be non-empty, got {len(healthy_days)}"
        self.healthy_days = healthy_days
        self.healthy_days_num = len(healthy_days)
        #compute nutrition avarages
        self.healthy_days_with_nutrition = [healthy_day for healthy_day in self.healthy_days
                                            if healthy_day.nutrition_day.consumed]
        self.healthy_days_with_nutrition_number = len(self.healthy_days_with_nutrition)
        #compute avarages
        ##nutrition
        self.avarage_fat = round(sum( healthy_day.nutrition_day.total_fat
                                      for healthy_day in self.healthy_days_with_nutrition)/
                            self.healthy_days_with_nutrition_number, 2)
        self.avarage_saturated_fat = round((sum(healthy_day.nutrition_day.total_saturated_fat for healthy_day in
                                              self.healthy_days_with_nutrition) / self.healthy_days_with_nutrition_number),2)
        self.avarage_fiber = round((sum( healthy_day.nutrition_day.total_fiber for healthy_day in self.healthy_days_with_nutrition)/
                            self.healthy_days_with_nutrition_number),2)
        self.avarage_protein = round((sum( healthy_day.nutrition_day.total_protein for healthy_day in self.healthy_days_with_nutrition)/
                            self.healthy_days_with_nutrition_number),2)
        self.avarage_carbohydrate = round((sum( healthy_day.nutrition_day.total_carbohydrate for healthy_day in
                                              self.healthy_days_with_nutrition)/self.healthy_days_with_nutrition_number),2)
        self.avarage_sugar = round((sum( healthy_day.nutrition_day.total_sugar for healthy_day in
                                              self.healthy_days_with_nutrition)/self.healthy_days_with_nutrition_number),2)
        ##exercise
        self.total_exercise = sum( healthy_day.exercise_minutes for healthy_day in self.healthy_days )
        self.avarage_exercise = round(self.total_exercise/self.healthy_days_num,2)
        ##weight
        self.weight_number = len([healthy_day.weight for healthy_day in self.healthy_days if healthy_day.weight > 0])
        self.avarage_weight = round((sum( healthy_day.weight for healthy_day in self.healthy_days)/
                                    self.weight_number),2)
        ##fat by kg
        self.fat_by_kg = round(self.avarage_fat/self.avarage_weight,2)
        self.protein_by_kg = round(self.avarage_protein/self.avarage_weight,2)


class HealthyWeek(HealthyDayGroup):
    def __init__(self, year, week_num, healthy_days:List[HealthyDay]):
        #todo: for human readability, add month and days dates in the week. e.g 10-17
        self.id = f"{year}-{week_num}"
        #get month, start and end day
        first_day_of_week_date = date.fromisocalendar(int(year),int(week_num),1)
        first_day_of_week =  first_day_of_week_date.day
        month = first_day_of_week_date.month
        last_day_of_week = date.fromisocalendar(int(year),int(week_num),7).day
        self.month = month
        self.days_range = f"{first_day_of_week}-{last_day_of_week}"
        # assert healthy days are in the right week
        for healthy_day in healthy_days:
            year, month, day = healthy_day.get_year_month_day()
            healthy_day_date = datetime.strptime(f"{year}{month}{day}", '%Y%m%d')
            healthy_day_week = healthy_day_date.isocalendar()[1]
            assert f"{year}-{healthy_day_week}" == self.id, (f"Healthy day {year}-{healthy_day_week} is not in week "
                                                             f"{self.id}")
        super().__init__(healthy_days)

    def __str__(self):
        return (
            f"Week ID: {self.id} | Month: {self.month} | Days: {self.days_range} |"
            f"Healthy days: {self.healthy_days_num} | Healthy days with nutrition: "
            f"{self.healthy_days_with_nutrition_number} | Avarage fat: {self.avarage_fat} | Avarage saturated: "
            f"{self.avarage_saturated_fat} | Avarage fiber {self.avarage_fiber} | Avarage protein: "
            f"{self.avarage_protein} | Avarage carbohydrate: {self.avarage_carbohydrate} | "
            f"Avarage sugar: {self.avarage_sugar} | Total Exercise: {self.total_exercise} | Avarage exercise:"
            f"{self.avarage_exercise} | Avarage weight: {self.avarage_weight}"
        )



