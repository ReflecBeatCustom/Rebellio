from .. import models

def get_constant(name):
    constants = models.Constants.objects.filter(namevar=name)
    if len(constants) == 0:
        return ''

    return constants[0].value