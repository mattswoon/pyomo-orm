from pyomo.environ import AbstractModel, NonNegativeReals
from .models import Food, FoodNutrientAmount, Nutrient

infinity = float('inf')

diet = AbstractModel()

# Sets
diet.food = Food.create_set()
diet.nutrient = Nutrient.create_set()

# Params
Food.create_param(from_attr='cost')
FoodNutrientAmount.create_param(
    from_attr='amount',
    indexed_by=['food', 'nutrient']
)
Nutrient.create_param(
    from_attr='lower_bound',
    within=NonNegativeReals,
    default=0.0
)
Nutrient.create_param(
    from_attr='upper_bound',
    within=NonNegativeReals,
    default=infinity
)
