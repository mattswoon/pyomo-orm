from pyomo_orm.core.problems import BaseProblem
from pyomo_orm.core.wrappers import ORMSet, ORMParam

from .models import Food, FoodNutrientAmount, Nutrient

infinity = float('inf')

class DietProblem(BaseProblem):
    # Sets
    foods = ORMSet(
        model=Food,
        queryset=Food.query().filter(Food.problem_run_id is None)
    )
    nutrients = ORMSet(
        model=Nutrient,
        queryset=Nutrient.query().filter(Nutrient.problem_run_id is None)
    )

    # Params
    cost = ORMParam(
        'foods',
        model=Food,
        from_attr='cost'
    )
    volume_per_serving = ORMParam(
        'foods',
        model=Food,
        from_attr='volume_per_serving'
    )
    amount = ORMParam(
        'foods',
        'nutrients',
        model=FoodNutrientAmount
        from_attr='amount',
        indexed_by=['food_id', 'nutrient_id']
    )
    nutrient_lower_bound = ORMParam(
        'nutrients',
        model=Nutrient,
        from_attr='lower_bound',
        within=NonNegativeReals,
        default=0.0
    )
    nutrient_upper_bound = ORMParam(
        'nutrients',
        model=Nutrient,
        from_attr='upper_bound',
        within=NonNegativeReals,
        default=infinity
    )



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
