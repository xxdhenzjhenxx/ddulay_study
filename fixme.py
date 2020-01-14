#!/bin/env python3

class Person:
    def __init__ (self, name, **kwargs):
        supported_kwargs = ['social', 'var1', 'var2','var3']
        self.name = name
        for key in supported_kwargs:
            if kwargs.get(key, False):
                print(f"I understand {key}")
                if key == 'social': self.social = kwargs[key]
                if key == 'var1': self.var1 = kwargs[key]
                if key == 'var2': self.var2 = kwargs[key]
                if key == 'var3': self.var3 = kwargs[key]

    def say(self, word):
        print(word)

    def whatareyoumadeof(self, *args, **kwargs):
        argc=0
        for arg in args:
            argc+=1
            print(f'arg{argc}: {arg}')

        if kwargs:
            print("\nYou sent me dictionary stuff".title())
            for k, v in kwargs.items():
                print(f"{k}: {v}")


Billy = Person('Billy', social = 123456789, var1 = 'apples are good', var2 = 'bananas are fine', var3 = 'carrots are gross')
print(Billy.var1)
print(Billy.var2)
print(Billy.var3)

Billy.say('Hello world!\n\nLove,\n\n{}\n\n'.format(Billy.name))
Billy.whatareyoumadeof(1, 2, "three", ['apple', 'banana', 'carrot'], thing1 = 'blue', thing2 = 'red', thing3 = ['orange', 'yellow', 'green'])
print(f"\n\nMy social is {Billy.social}")