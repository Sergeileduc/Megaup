"""Doc."""


class MegaNode(dict):

    # def __init__(self, *args, **kwargs):
    #     super().__init__(*args, **kwargs)

    def get_name(self):
        return list(self.values())[0]['a']['n']


my_dict = {'sAxkwY5Z': {'a': {'n': 'Documents'},
                        'h': 'sAxkwY5Z',
                        'k': (37382039, 2746539309, 131188102, 3776792922),
                        'key': (37382039, 2746539309, 131188102, 3776792922),
                        'p': 'cdo00QjI',
                        't': 1,
                        'ts': 1579267652,
                        'u': 'fwIpP4wksKg'}
           }


# my_node = MegaNode(my_dict)

# print(type(my_node))
# print(my_node)
# print(my_node.get_name())
# print(type(my_node.get_name()))

print(MegaNode(my_dict).get_name())
