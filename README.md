# AI-Powered Health & Fitness Application

A comprehensive health and fitness application that provides personalized nutrition and workout recommendations using Google Gemini AI.

## Features

### Core Functionality
- **Personalized Calorie Calculation**: BMR and TDEE calculations based on user profile
- **Macro Distribution**: Custom protein, carbs, fats, and fiber recommendations
- **Daily Steps Goal**: Activity-based step recommendations
- **AI-Powered Meal Plans**: Personalized meal suggestions using Google Gemini
- **Smart Food Suggestions**: Dynamic food recommendations based on nutritional gaps
- **Workout Plans**: Customized exercise routines for different goals

### Health Goals Support
- Weight Loss
- Muscle Gain  
- Fat Loss
- General Wellness
- Diabetic Friendly
- Heart Health

### Advanced Features
- **Dynamic Personalization**: Uses Google Gemini AI for intelligent recommendations
- **Goal-Oriented Customization**: Adjusts calories, macros, and advice based on specific goals
- **Real-time Form Validation**: Input validation and auto-save functionality
- **Responsive Design**: Works on desktop, tablet, and mobile devices
- **Data Persistence**: Save and load user plans locally

## Installation

1. **Clone the repository**
   ```bash
   cd s3_assignment
   ```

2. **Install dependencies**
   ```bash
   uv install
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your Google Gemini API key:
   ```
   GEMINI_API_KEY=your_actual_api_key_here
   ```

4. **Get Google Gemini API Key**
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create a new API key
   - Copy the key to your `.env` file

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000`

## Usage

1. **Fill out the health assessment form** with your:
   - Basic info (age, weight, height, gender)
   - Lifestyle and profession details
   - Physical activity level
   - Health goals
   - Food preferences

2. **Get your personalized plan** including:
   - Daily calorie requirements
   - Macro breakdown (protein, carbs, fats, fiber)
   - Daily steps recommendation
   - AI-generated meal plan
   - Smart food suggestions
   - Workout recommendations

3. **Use advanced features**:
   - Regenerate suggestions for variety
   - Save your plan for future reference
   - Auto-saved form data for convenience

## Technology Stack

- **Backend**: Python Flask
- **AI Integration**: Google Gemini API
- **Frontend**: HTML5, CSS3, JavaScript (Vanilla)
- **Styling**: Custom CSS with responsive design
- **Icons**: Font Awesome
- **Data Storage**: Local Storage (browser-based)

## API Endpoints

- `GET /` - Main application page
- `POST /calculate` - Calculate nutrition and fitness requirements
- `POST /smart_suggestions` - Generate AI-powered food suggestions

## Health Calculations

### BMR (Basal Metabolic Rate)
Uses Mifflin-St Jeor Equation:
- Men: BMR = 10 × weight + 6.25 × height - 5 × age + 5
- Women: BMR = 10 × weight + 6.25 × height - 5 × age - 161

### TDEE (Total Daily Energy Expenditure)
BMR × Activity Factor:
- Sedentary: 1.2
- Lightly Active: 1.375
- Moderately Active: 1.55
- Very Active: 1.725
- Extremely Active: 1.9

### Goal-Based Adjustments
- Weight Loss: -500 calories
- Fat Loss: -300 calories
- Muscle Gain: +300 calories
- Diabetic Friendly: -200 calories
- General Wellness: No adjustment
- Heart Health: No adjustment

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For support or questions, please open an issue in the repository.
