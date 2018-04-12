from pyomo_orm.core.models import Base, ProblemRunMixin
from sqlalchemy import Column, Integer, String, Float, ForeignKey
from sqlalchemy.orm import relationship


class Food(ProblemRunMixin, Base):
    __tablename__ = 'foods'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    cost = Column(Float)
    volume_per_serving = Column(Float)
    nutrient_amounts = relationship('FoodNutrientAmount')
    amount_in_diet = Column(Integer, nullable=True)

    def __repr__(self):
        return '<Food: {}>'.format(
            self.name
        )


class FoodNutrientAmount(ProblemRunMixin, Base):
    __tablename__ = 'food_nutrient_amounts'

    id = Column(Integer, primary_key=True)
    food_id = Column(Integer, ForeignKey('foods.id'))
    nutrient_id = Column(Integer, ForeignKey('nutrients.id'))
    amount = Column(Float)

    food = relationship('Food', back_populates='nutrient_amounts')
    nutrient = relationship('Nutrient')

    def __repr__(self):
        return '<Amount: {amount} of {nutrient} in {food}'.format(
            amount=self.amount,
            nutrient=self.nutrient.name,
            food=self.food.name
        )


class Nutrient(ProblemRunMixin, Base):
    __tablename__ = 'nutrients'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)

    def __repr__(self):
        return '<Nutrient: {}>'.format(self.name)
