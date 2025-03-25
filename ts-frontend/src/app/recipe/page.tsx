"use client";

export default function recipe() {
    return (
        <div className="bg-emerald-50 min-h-screen p-8">
            <h1 className="text-4xl font-bold text-center mb-8 text-emerald-800">
                GEN AI Recipe Maker
            </h1>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8 min-h-[60vh]">
            {/* Left Card (User Preferences) */}
            <div className="bg-white p-8 rounded-xl shadow-lg flex flex-col">
                <h2 className="text-xl font-semibold mb- text-center">Curate your recipe!</h2>
                {/* Preferences form will go here */}
            </div>
    
            {/* Right Card (Recipe Display) */}
            <div className="bg-white p-8 rounded-xl shadow-lg flex flex-col">
                <h2 className="text-xl font-semibold mb-4 text-center">Generated Recipe</h2>
                {/* Recipe content will go here */}
            </div>
            </div>
    
            {/* Generate Recipe Button */}
            <div className="flex justify-center mt-8">
            <button
                className="bg-emerald-600 text-white font-semibold py-2 px-6 rounded-lg shadow-lg hover:bg-emerald-700 transition duration-300"
                onClick={() => {
                // Logic for generating the recipe will go here
                }}
            >
                Generate Recipe
            </button>
            </div>
        </div>
    )
}