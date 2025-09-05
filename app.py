from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
import json
import math

load_dotenv()

try:
    import google.generativeai as genai
    genai.configure(api_key=os.getenv('GEMINI_API_KEY'))
    model = genai.GenerativeModel('gemini-pro')
except Exception:
    genai = None
    model = None

app = Flask(__name__)

# Configure Google Gemini API

class HealthCalculator:
    @staticmethod
    def calculate_bmr(weight, height, age, gender):
        """Calculate Basal Metabolic Rate using Mifflin-St Jeor Equation"""
        if gender.lower() == 'male':
            bmr = 10 * weight + 6.25 * height - 5 * age + 5
        else:
            bmr = 10 * weight + 6.25 * height - 5 * age - 161
        return bmr
    
    @staticmethod
    def calculate_tdee(bmr, activity_level):
        """Calculate Total Daily Energy Expenditure"""
        activity_multipliers = {
            'sedentary': 1.2,
            'lightly_active': 1.375,
            'moderately_active': 1.55,
            'very_active': 1.725,
            'extremely_active': 1.9
        }
        return bmr * activity_multipliers.get(activity_level, 1.2)
    
    @staticmethod
    def calculate_macros(calories, goal):
        """Calculate macronutrient distribution based on goal"""
        macro_ratios = {
            'weight_loss': {'protein': 0.35, 'carbs': 0.30, 'fats': 0.35},
            'muscle_gain': {'protein': 0.30, 'carbs': 0.45, 'fats': 0.25},
            'fat_loss': {'protein': 0.40, 'carbs': 0.25, 'fats': 0.35},
            'general_wellness': {'protein': 0.25, 'carbs': 0.45, 'fats': 0.30},
            'diabetic_friendly': {'protein': 0.25, 'carbs': 0.35, 'fats': 0.40},
            'heart_health': {'protein': 0.25, 'carbs': 0.50, 'fats': 0.25}
        }
        
        ratios = macro_ratios.get(goal, macro_ratios['general_wellness'])
        
        protein_cals = calories * ratios['protein']
        carbs_cals = calories * ratios['carbs']
        fats_cals = calories * ratios['fats']
        
        return {
            'protein': round(protein_cals / 4),  # 4 calories per gram
            'carbs': round(carbs_cals / 4),      # 4 calories per gram
            'fats': round(fats_cals / 9),        # 9 calories per gram
            'fiber': round(14 * calories / 1000)  # 14g per 1000 calories
        }
    
    @staticmethod
    def calculate_steps(goal, activity_level):
        """Calculate recommended daily steps"""
        base_steps = {
            'sedentary': 8000,
            'lightly_active': 10000,
            'moderately_active': 12000,
            'very_active': 15000,
            'extremely_active': 18000
        }
        
        goal_modifiers = {
            'weight_loss': 1.3,
            'fat_loss': 1.4,
            'muscle_gain': 1.1,
            'general_wellness': 1.0,
            'diabetic_friendly': 1.2,
            'heart_health': 1.25
        }
        
        base = base_steps.get(activity_level, 10000)
        modifier = goal_modifiers.get(goal, 1.0)
        
        return round(base * modifier)

class AIPersonalizer:
    def __init__(self):
        self.model = model  # may be None if gemini isn't configured

    def _use_ai(self, prompt, fallback_fn):
        if not self.model:
            return fallback_fn()
        try:
            response = self.model.generate_content(prompt)
            return (response.text or '').strip() or fallback_fn()
        except Exception:
            return fallback_fn()

    def generate_meal_plan(self, user_data, nutrition_requirements):
        prompt = f"""
        Create a personalized daily meal plan for a {user_data['age']}-year-old {user_data['gender']} 
        who is {user_data['height']}cm tall, weighs {user_data['weight']}kg, works as a {user_data['profession']}, 
        has a {user_data['lifestyle']} lifestyle, and engages in {user_data['physical_activities']}.
        Goal: {user_data['health_goals']}
        Food Preferences: {user_data['food_preferences']}
        Nutritional Requirements (kcal/g): Calories {nutrition_requirements['calories']}, Protein {nutrition_requirements['protein']}, Carbs {nutrition_requirements['carbs']}, Fats {nutrition_requirements['fats']}, Fiber {nutrition_requirements['fiber']}
        Output JSON with keys: breakfast, snack1, lunch, snack2, dinner. Each value should include items and portions.
        """
        return self._use_ai(prompt, lambda: self._default_meal_plan(user_data['health_goals']))

    def generate_food_suggestions(self, user_data, current_nutrition):
        prompt = f"""
        Suggest 5 smart foods for goal {user_data['health_goals']} honoring preferences: {user_data['food_preferences']}.
        Current target intake: {current_nutrition}. Explain why each food helps.
        """
        return self._use_ai(prompt, lambda: self._default_food_suggestions(user_data['health_goals']))

    def generate_workout_advice(self, user_data, steps_goal):
        prompt = f"""
        Build a weekly workout plan for a {user_data['age']}-year-old {user_data['gender']} with activities {user_data['physical_activities']}, lifestyle {user_data['lifestyle']}, goal {user_data['health_goals']}. Include daily steps target {steps_goal}, sets/reps/mins, recovery tips.
        """
        return self._use_ai(prompt, lambda: self._default_workout_plan(user_data['health_goals']))
    
    def _default_meal_plan(self, goal):
        plans = {
            'weight_loss': {
                'breakfast': 'Greek yogurt with berries and nuts',
                'lunch': 'Grilled chicken salad with olive oil dressing',
                'dinner': 'Baked salmon with roasted vegetables',
                'snack1': 'Apple with almond butter',
                'snack2': 'Handful of mixed nuts'
            },
            'muscle_gain': {
                'breakfast': 'Protein smoothie with banana and oats',
                'lunch': 'Chicken breast with quinoa and vegetables',
                'dinner': 'Lean beef with sweet potato',
                'snack1': 'Protein bar',
                'snack2': 'Greek yogurt with granola'
            }
        }
        return json.dumps(plans.get(goal, plans['weight_loss']))
    
    def _default_food_suggestions(self, goal):
        suggestions = {
            'weight_loss': ['Leafy greens', 'Lean proteins', 'Berries', 'Nuts', 'Green tea'],
            'muscle_gain': ['Protein powder', 'Eggs', 'Quinoa', 'Avocado', 'Tuna'],
            'heart_health': ['Salmon', 'Oats', 'Blueberries', 'Olive oil', 'Dark chocolate']
        }
        return str(suggestions.get(goal, suggestions['weight_loss']))
    
    def _default_workout_plan(self, goal):
        plans = {
            'weight_loss': 'Focus on cardio: 30min daily walking, 3x/week strength training',
            'muscle_gain': 'Strength training 4x/week, moderate cardio 2x/week',
            'heart_health': 'Aerobic exercise 150min/week, strength training 2x/week'
        }
        return plans.get(goal, plans['weight_loss'])

# Initialize AI personalizer
ai_personalizer = AIPersonalizer()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate_requirements():
    try:
        data = request.get_json()
        
        # Extract user data
        user_data = {
            'age': int(data['age']),
            'weight': float(data['weight']),
            'height': float(data['height']),
            'gender': data['gender'],
            'profession': data['profession'],
            'lifestyle': data['lifestyle'],
            'physical_activities': data['physical_activities'],
            'health_goals': data['health_goals'],
            'food_preferences': data['food_preferences']
        }
        
        # Calculate BMR and TDEE
        bmr = HealthCalculator.calculate_bmr(
            user_data['weight'], 
            user_data['height'], 
            user_data['age'], 
            user_data['gender']
        )
        
        activity_level = data.get('activity_level', 'moderately_active')
        tdee = HealthCalculator.calculate_tdee(bmr, activity_level)
        
        # Adjust calories based on goal
        goal_adjustments = {
            'weight_loss': -500,
            'fat_loss': -300,
            'muscle_gain': 300,
            'general_wellness': 0,
            'diabetic_friendly': -200,
            'heart_health': 0
        }
        
        target_calories = tdee + goal_adjustments.get(user_data['health_goals'], 0)
        
        # Calculate macronutrients
        macros = HealthCalculator.calculate_macros(target_calories, user_data['health_goals'])
        
        # Calculate steps recommendation
        steps_goal = HealthCalculator.calculate_steps(user_data['health_goals'], activity_level)
        
        # Prepare nutrition requirements
        nutrition_requirements = {
            'calories': round(target_calories),
            'protein': macros['protein'],
            'carbs': macros['carbs'],
            'fats': macros['fats'],
            'fiber': macros['fiber']
        }
        
        # Generate AI-powered recommendations
        meal_plan = ai_personalizer.generate_meal_plan(user_data, nutrition_requirements)
        food_suggestions = ai_personalizer.generate_food_suggestions(user_data, nutrition_requirements)
        workout_advice = ai_personalizer.generate_workout_advice(user_data, steps_goal)
        
        results = {
            'bmr': round(bmr),
            'tdee': round(tdee),
            'target_calories': nutrition_requirements['calories'],
            'macros': macros,
            'steps_goal': steps_goal,
            'meal_plan': meal_plan,
            'food_suggestions': food_suggestions,
            'workout_advice': workout_advice,
            'user_data': user_data
        }
        
        return jsonify(results)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/smart_suggestions', methods=['POST'])
def smart_suggestions():
    try:
        data = request.get_json()
        current_nutrition = data.get('current_nutrition', {})
        user_data = data.get('user_data', {})
        
        suggestions = ai_personalizer.generate_food_suggestions(user_data, current_nutrition)
        
        return jsonify({'suggestions': suggestions})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
