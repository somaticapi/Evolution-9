from brain.NN import neural_network
from evolution import operators
from evolution.genome import song

class evolution(object):
    def __init__(self, name, evaluator, population_size, store, generation_count = 0, state='uninitialized'):
        self.store = store
        self.name = name
        self.evaluator = neural_network.get_saved(evaluator, store)
        self.population_size = population_size
        self.generation_count = generation_count
        self.state = state
        if self.state != 'uninitialized':
            self.get_current_generation()
        else:
            self.current_generation = None

        self.save()

    def save(self):
        self.store.save_evolution(self.name,
                                  self.population_size,
                                  self.evaluator.name,
                                  self.generation_count,
                                  self.state)
        return

    def save_genomes(self):
        for g in self.current_generation:
            self.store.save_genome(g.name,
                                   g.genome,
                                   g.evolution,
                                   g.generation,
                                   g.individual_id,
                                   g.parent_1,
                                   g.parent_2,
                                   g.grade,
                                   g.status)
        return

    @classmethod
    def get_saved(cls, name, store):
        result = store.get_evolution(name)

        return cls(result[0], result[3], result[1], store, result[2], result[4]) if result else None

    @classmethod
    def get_list(cls, store):
        result = store.get_evolution_list()

        return [x[0] for x in result] if result else None

    def initialize(self, console = None):
        self.current_generation = []

        for i in xrange(self.population_size):
            g = song(operators.random_genome(), self.name, 0, i)
            self.current_generation.append(g)

        self.state = 'evaluation'
        self.save_genomes()
        self.save()

        if console:
            console('%s is initialized'%self.name)
        return

    @property
    def initialized(self):
        return self.state != 'uninitialized'

    def get_current_generation(self):
        result = self.store.get_genomes(self.name, self.generation_count)

        if result:
            self.current_generation = []

            for i in result:
                g = song(i[1], i[2], i[3], i[4], i[5], i[6], i[7], i[8])
                self.current_generation.append(g)

        return

    def evaluate(self, console = None):
        self.results = []
        for g in self.current_generation:
            result = self.evaluator.evaluate(g.int_list)
            g.grade = result
            if console:
                console('%s evaluation result: %f'%(g.name, result))

        self.current_generation = sorted(self.current_generation, key=lambda x: x.grade, reverse=True)
        for i in range(self.population_size):
            if i < self.population_size/2:
                self.current_generation[i].status = 'selected'
            else:
                self.current_generation[i].status = 'eliminated'
        self.state = 'select'

        if console:
            console('Generation %d of %s : evaluation complete'%(self.generation_count, self.name))
        return

    def apply_selection(self, console = None):
        self.save_genomes()

        self.current_generation = self.current_generation[:self.population_size/2]
        self.state = 'reproduce'

        self.save()

        console('%s : applied selection on generation %d'%(self.name, self.generation_count))
        
        return
