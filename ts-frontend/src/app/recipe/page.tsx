"use client";

import React, { useState } from 'react';
import { Card, CardContent, Button, Typography, FormControl, InputLabel, Select, MenuItem, Grid, Checkbox, ListItemText } from '@mui/material';
import RestaurantIcon from '@mui/icons-material/Restaurant';
import { useRouter } from 'next/router';
import { CheckBox } from '@mui/icons-material';
import RecipeDisplay from './RecipeDisplay'

export default function recipe() {

    // State to manage the selected options
    const [mealType, setMealType] = useState('None');
    const [dietaryNeeds, setDietaryNeeds] = useState<string[]>([]);
    const [cuisineType, setCuisineType] = useState('None');
    const [mainIngredient, setMainIngredient] = useState('None');
    const [dishType, setDishType] = useState('None');

    // State to hold the recipe data
    const [recipeData, setRecipeData] = useState<any>(null);

    const meal_type = ["Appetizer", "Breakfast", "Dessert", "Dinner", "Lunch", "Side Dish", "Snack", "None"]
    const dietary_needs = ["Diabetic-friendly", "Gluten-free", "Healthy", "Lactose-free", "Low-calorie", "Low-carb", "Low-fat", "Low-sodium", "Vegan", "Vegetarian"]
    const cuisine_type = ["Chinese", "French", "Greek", "Indian", "Italian", "Mexican", "Southern", "None"]
    const main_ingredient = ["Beef", "Bread", "Chicken", "Fish", "Pasta", "Pork", "Rice", "Shrimp", "None"]
    const dish_type = ["Cake", "Casserole", "Cookie", "Pie", "Salad", "Soup", "None"]

    const handleChange = (setter: React.Dispatch<React.SetStateAction<any>>) => (event: React.ChangeEvent<{ value: unknown }>) => {
        setter(event.target.value);
    };

    const handleDietaryNeedsChange = (event: React.ChangeEvent<{ value: unknown }>) => {
        setDietaryNeeds(event.target.value as string[]); // Update state with selected values
      };

    const renderSelectOptions = (options: string[]) => {
        return options.map((option, index) => (
            <MenuItem key={index} value={option}>
            {option}
            </MenuItem>
        ));
    };

     // Function to send the POST request
    const handleGenerateRecipe = async () => {
        const payload = {
        mealType,
        dietaryNeeds,
        cuisineType,
        mainIngredient,
        dishType,
        };

        try {
        const response = await fetch('http://127.0.0.1:8000/getrecipe', {
            method: 'POST',
            headers: {
            'Content-Type': 'application/json',
            },
            body: JSON.stringify(payload), // Send state data as JSON
        });

        if (response.ok) {
            const result = await response.json(); // Parsing JSON response
            setRecipeData(result);
            console.log('Recipe generated:', result);
            // Handle the result (display the recipe, etc.)
        } else {
            console.error('Error generating recipe');
        }
        } catch (error) {
        console.error('Network error:', error);
        }
    };

    return (
        <div className="bg-emerald-50 min-h-screen p-8">
            <h1 className="text-4xl font-bold text-center mb-8 text-emerald-800">
                GEN AI Recipe Maker
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 min-h-[60vh]">
            {/* Left Card (User Preferences) */}
            <Card className="flex flex-col" raised>
            <CardContent>
                <Typography variant="h4" component="h1" align="center" gutterBottom>
                Curate Your Recipe!
                </Typography>

                {/* Preferences Form */}
                <Grid container spacing={3}>
                {/* Meal Type */}
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                    <InputLabel>Meal Type</InputLabel>
                    <Select
                        value={mealType}
                        onChange={handleChange(setMealType)}
                        label="Meal Type"
                    >
                        {renderSelectOptions(meal_type)}
                    </Select>
                    </FormControl>
                </Grid>

                {/* Dietary Needs */}
                <Grid item xs={12} sm={6}>
                <FormControl fullWidth>
                    <InputLabel>Dietary Needs</InputLabel>
                    <Select
                    multiple
                    value={dietaryNeeds}
                    onChange={handleDietaryNeedsChange}
                    renderValue={(selected) => selected.join(', ')} // Display selected values as comma-separated
                    >
                    {dietary_needs.map((need, index) => (
                        <MenuItem key={index} value={need}>
                        <Checkbox checked={dietaryNeeds.indexOf(need) > -1} />
                        <ListItemText primary={need} />
                        </MenuItem>
                    ))}
                    </Select>
                </FormControl>
                </Grid>

                {/* Cuisine Type */}
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                    <InputLabel>Cuisine Type</InputLabel>
                    <Select
                        value={cuisineType}
                        onChange={handleChange(setCuisineType)}
                        label="Cuisine Type"
                    >
                        {renderSelectOptions(cuisine_type)}
                    </Select>
                    </FormControl>
                </Grid>

                {/* Main Ingredient */}
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                    <InputLabel>Main Ingredient</InputLabel>
                    <Select
                        value={mainIngredient}
                        onChange={handleChange(setMainIngredient)}
                        label="Main Ingredient"
                    >
                        {renderSelectOptions(main_ingredient)}
                    </Select>
                    </FormControl>
                </Grid>

                {/* Dish Type */}
                <Grid item xs={12} sm={6}>
                    <FormControl fullWidth>
                    <InputLabel>Dish Type</InputLabel>
                    <Select
                        value={dishType}
                        onChange={handleChange(setDishType)}
                        label="Dish Type"
                    >
                        {renderSelectOptions(dish_type)}
                    </Select>
                    </FormControl>
                </Grid>
                </Grid>
            </CardContent>
            </Card>

            {/* Right Card (Recipe Display) */}
            <Card className="flex flex-col" raised>
            <CardContent>
                <Typography variant="h4" component="h2" align="center" gutterBottom>
                    Generated Recipe
                </Typography>

                <RecipeDisplay recipeData={recipeData} />
            </CardContent>
            </Card>
        </div>

        {/* Generate Recipe Button */}
        <div className="flex justify-center mt-8">
            <Button
            variant="contained"
            startIcon={<RestaurantIcon />}
            onClick={handleGenerateRecipe}
            size='large'
            className="bg-emerald-600 hover:bg-emerald-700 transition duration-300"
            >
            Generate Recipe
            </Button>
        </div>
        </div>
    )
}