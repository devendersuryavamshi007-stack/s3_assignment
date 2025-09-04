document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('healthForm');
    const loadingDiv = document.getElementById('loadingDiv');
    const resultsDiv = document.getElementById('results');
    const regenerateBtn = document.getElementById('regenerateBtn');
    const saveBtn = document.getElementById('saveBtn');
    
    let currentUserData = null;
    let currentResults = null;

    form.addEventListener('submit', function(e) {
        e.preventDefault();
        calculateRequirements();
    });

    regenerateBtn.addEventListener('click', function() {
        if (currentUserData) {
            generateSmartSuggestions();
        }
    });

    saveBtn.addEventListener('click', function() {
        savePlan();
    });

    function calculateRequirements() {
        const formData = new FormData(form);
        const data = Object.fromEntries(formData);
        
        // Add activity level based on lifestyle and physical activities
        data.activity_level = data.lifestyle;
        
        currentUserData = data;
        
        // Show loading
        loadingDiv.style.display = 'block';
        resultsDiv.style.display = 'none';
        
        // Scroll to loading
        loadingDiv.scrollIntoView({ behavior: 'smooth' });

        fetch('/calculate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            currentResults = data;
            displayResults(data);
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to calculate requirements. Please try again.');
        })
        .finally(() => {
            loadingDiv.style.display = 'none';
        });
    }

    function displayResults(data) {
        // Update metric cards
        document.getElementById('calories').textContent = data.target_calories;
        document.getElementById('protein').textContent = data.macros.protein + 'g';
        document.getElementById('carbs').textContent = data.macros.carbs + 'g';
        document.getElementById('fats').textContent = data.macros.fats + 'g';
        document.getElementById('fiber').textContent = data.macros.fiber + 'g';
        document.getElementById('steps').textContent = data.steps_goal.toLocaleString();

        // Update metabolic info
        document.getElementById('bmr').textContent = data.bmr;
        document.getElementById('tdee').textContent = data.tdee;

        // Display AI-generated content
        document.getElementById('mealPlan').textContent = formatMealPlan(data.meal_plan);
        document.getElementById('foodSuggestions').textContent = data.food_suggestions;
        document.getElementById('workoutPlan').textContent = data.workout_advice;

        // Show results with animation
        resultsDiv.style.display = 'block';
        resultsDiv.classList.add('fade-in');
        resultsDiv.scrollIntoView({ behavior: 'smooth' });
    }

    function formatMealPlan(mealPlanText) {
        try {
            // Try to parse as JSON first
            const mealPlan = JSON.parse(mealPlanText);
            let formatted = '';
            for (const [meal, description] of Object.entries(mealPlan)) {
                formatted += `${meal.charAt(0).toUpperCase() + meal.slice(1)}:\n${description}\n\n`;
            }
            return formatted;
        } catch (e) {
            // If not JSON, return as is
            return mealPlanText;
        }
    }

    function generateSmartSuggestions() {
        if (!currentUserData || !currentResults) return;

        loadingDiv.style.display = 'block';
        
        const requestData = {
            user_data: currentUserData,
            current_nutrition: {
                calories: currentResults.target_calories,
                protein: currentResults.macros.protein,
                carbs: currentResults.macros.carbs,
                fats: currentResults.macros.fats
            }
        };

        fetch('/smart_suggestions', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(requestData)
        })
        .then(response => response.json())
        .then(data => {
            if (data.error) {
                throw new Error(data.error);
            }
            document.getElementById('foodSuggestions').textContent = data.suggestions;
            showSuccess('Smart suggestions updated!');
        })
        .catch(error => {
            console.error('Error:', error);
            showError('Failed to generate new suggestions. Please try again.');
        })
        .finally(() => {
            loadingDiv.style.display = 'none';
        });
    }

    function savePlan() {
        if (!currentResults) return;

        const planData = {
            date: new Date().toISOString().split('T')[0],
            userData: currentUserData,
            results: currentResults
        };

        // Save to localStorage
        localStorage.setItem('healthPlan_' + planData.date, JSON.stringify(planData));
        
        showSuccess('Plan saved successfully! You can access it anytime.');
    }

    function showError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error';
        errorDiv.textContent = message;
        
        const container = document.querySelector('.container');
        container.insertBefore(errorDiv, container.firstChild);
        
        setTimeout(() => {
            errorDiv.remove();
        }, 5000);
    }

    function showSuccess(message) {
        const successDiv = document.createElement('div');
        successDiv.className = 'success';
        successDiv.textContent = message;
        
        const container = document.querySelector('.container');
        container.insertBefore(successDiv, container.firstChild);
        
        setTimeout(() => {
            successDiv.remove();
        }, 3000);
    }

    // Add input validation and formatting
    const weightInput = document.getElementById('weight');
    const heightInput = document.getElementById('height');
    const ageInput = document.getElementById('age');

    weightInput.addEventListener('input', function() {
        if (this.value < 20) this.value = 20;
        if (this.value > 300) this.value = 300;
    });

    heightInput.addEventListener('input', function() {
        if (this.value < 100) this.value = 100;
        if (this.value > 250) this.value = 250;
    });

    ageInput.addEventListener('input', function() {
        if (this.value < 13) this.value = 13;
        if (this.value > 120) this.value = 120;
    });

    // Auto-save form data
    const formInputs = form.querySelectorAll('input, select, textarea');
    formInputs.forEach(input => {
        input.addEventListener('change', function() {
            const formData = new FormData(form);
            const data = Object.fromEntries(formData);
            localStorage.setItem('healthFormData', JSON.stringify(data));
        });
    });

    // Load saved form data
    const savedFormData = localStorage.getItem('healthFormData');
    if (savedFormData) {
        try {
            const data = JSON.parse(savedFormData);
            Object.entries(data).forEach(([key, value]) => {
                const field = form.querySelector(`[name="${key}"]`);
                if (field) {
                    field.value = value;
                }
            });
        } catch (e) {
            console.log('Failed to load saved form data');
        }
    }

    // Add BMI calculator as bonus feature
    function calculateBMI(weight, height) {
        const heightInMeters = height / 100;
        return (weight / (heightInMeters * heightInMeters)).toFixed(1);
    }

    // Real-time BMI display
    function updateBMI() {
        const weight = parseFloat(weightInput.value);
        const height = parseFloat(heightInput.value);
        
        if (weight && height) {
            const bmi = calculateBMI(weight, height);
            let bmiCategory = '';
            
            if (bmi < 18.5) bmiCategory = 'Underweight';
            else if (bmi < 25) bmiCategory = 'Normal';
            else if (bmi < 30) bmiCategory = 'Overweight';
            else bmiCategory = 'Obese';
            
            // Show BMI if elements exist
            const bmiDisplay = document.getElementById('bmiDisplay');
            if (bmiDisplay) {
                bmiDisplay.textContent = `BMI: ${bmi} (${bmiCategory})`;
            }
        }
    }

    weightInput.addEventListener('input', updateBMI);
    heightInput.addEventListener('input', updateBMI);
});


