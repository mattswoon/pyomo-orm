
class SetDefinerMixin:

    def define_sets(self):
        for m in self.set_models:
            name = self._generate_set_name(m)
            setattr(
                self.pyomo_model,
                name,
                m.create_set(**kwargs)
            )

    def _generate_set_name(self, model):
        return '{}_set'.format(model.__name__.lower())
