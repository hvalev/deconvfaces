
import yaml


class ModelDescription:

    ''''
    Model Description file, which will contain all the variables required to ensure,
    selecting constrainted data from the dataset would still result in proper inputs for generation and testing
    Model is loaded and updated in different parts of the code, thus always needing to load it and update it if
    changes are made in different parts
    TODO probably also include a dedicated class, which gives you more clearly the options,
    which parts of the dataset to be used for testing and training
    TODO Could just have a 'template with already precompiled 'options'' -> caveat the actual keras model might also be defined here too; good -> many tests on networks

    '''

    def __init__(self):
        self.data = {}
        pass

    def __del__(self):
        pass

    def genPathFromModelName(self, model_path):
        path = model_path + '.modeldesc.yaml'
        self.data['path'] = path
        pass

    def importVariablesFromModelName(self):
        params_from_model = self.data.get('path').split('.')
        self.data['deconv_layers'] = int(params_from_model[3][1:])
        self.data['optimizer']= params_from_model[4]
        if params_from_model[1] == 'YaleFaces':
            self.use_yale = True
        elif params_from_model[1] == 'JAFFE':
            self.use_jaffe = True
        self.save()
        pass

    def save(self):
        with open(self.data['path'], "w") as f:
            yaml.dump(self.data, f)
        pass

    def loadFromPath(self, model_desc_path):
        with open(model_desc_path) as f:
            dataMap = yaml.safe_load(f)
            self.data = dataMap
        pass

    def print(self):
        with open(self.data.get('path')) as f:
            dataMap = yaml.safe_load(f)
            print(dataMap)
        pass

    def getPath(self):
        return self.data.get('path')

    def getAttr(self, attr):
        return self.data.get(attr)
        #return

    def setAttr(self, key, value):
        self.data[key] = value
        pass