import React, { useState } from 'react';
import { 
  Card, 
  Typography, 
  Tabs, 
  Tab, 
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableRow,
  Paper,
  Box
} from '@mui/material';

function TabPanel(props) {
  const { children, value, index, ...other } = props;

  return (
    <div
      role="tabpanel"
      hidden={value !== index}
      id={`recipe-tabpanel-${index}`}
      aria-labelledby={`recipe-tab-${index}`}
      {...other}
    >
      {value === index && (
        <Box p={3}>
          {children}
        </Box>
      )}
    </div>
  );
}

const RecipeDisplay = ({ recipeData }) => {
  const [value, setValue] = useState(0);

  const handleChange = (event, newValue) => {
    setValue(newValue);
  };

  if (!recipeData) {
    return (
      <Typography 
        variant="body1" 
        color="textSecondary" 
        align='center' 
        className="p-6 italic"
      >
        No recipe generated yet. Please generate a recipe.
      </Typography>
    );
  }

  return (
    <Card 
      raised 
      className="max-w-2xl mx-auto shadow-2xl rounded-2xl overflow-hidden bg-[#F5F5DC]" // Beige background
    >
      {/* Recipe Title */}
      <div className="bg-gradient-to-r from-blue-600 to-teal-500 text-white p-6 text-center">
        <Typography 
          variant="h4" 
          component="h2" 
          className="font-bold text-2xl"
        >
          {recipeData.Recipe_name}
        </Typography>
      </div>

      {/* Tabs */}
      <Tabs
        value={value}
        onChange={handleChange}
        variant="fullWidth"
        className="bg-gray-100"
        textColor="primary"
        indicatorColor="primary"
      >
        <Tab label="Ingredients" />
        <Tab label="Instructions" />
        <Tab label="Nutritional Insights" />
      </Tabs>

      {/* Ingredients Tab */}
      <TabPanel value={value} index={0}>
        <Paper 
          elevation={3} 
          className="bg-white p-4 rounded-lg"
        >
          <TableContainer>
            <Table>
              <TableBody>
                {recipeData.Ingredients.map((ingredient, index) => (
                  <TableRow 
                    key={index} 
                    hover 
                    className="hover:bg-blue-50"
                  >
                    <TableCell className="text-gray-800">
                      {ingredient}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </TabPanel>

      {/* Instructions Tab */}
      <TabPanel value={value} index={1}>
        <Paper 
          elevation={3} 
          className="bg-white p-4 rounded-lg"
        >
          <TableContainer>
            <Table>
              <TableBody>
                {recipeData['Step by step instructions'].map((step, index) => (
                  <TableRow 
                    key={index} 
                    hover 
                    className="hover:bg-teal-50"
                  >
                    <TableCell 
                      className="font-bold text-teal-600 pr-2 w-16 align-top"
                    >
                      Step {index + 1}
                    </TableCell>
                    <TableCell 
                      className="text-gray-800 w-full align-top"
                    >
                      {step.replace(/^\d+\.\s*/, '')}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          </TableContainer>
        </Paper>
      </TabPanel>

      {/* Nutritional Insights Tab */}
      <TabPanel value={value} index={2}>
        <Paper 
          elevation={3} 
          className="bg-white p-4 rounded-lg"
        >
          <Typography 
            variant="body2" 
            className="text-green-800"
          >
            {recipeData.Nutritional_note}
          </Typography>
        </Paper>
      </TabPanel>
    </Card>
  );
};

export default RecipeDisplay;