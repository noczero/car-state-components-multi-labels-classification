from models.car_physical_change_classifier import CarPhysicalChangeClassifier
from models.car_physical_change_explainer import CarPhysicalChangeExplainer

classifier_model = CarPhysicalChangeClassifier()
classifier_model.load_model()

def get_classifier_model() -> CarPhysicalChangeClassifier:
    return classifier_model


explainer_model = CarPhysicalChangeExplainer()
explainer_model.load_model()

def get_explainer_model() -> CarPhysicalChangeExplainer:
    return explainer_model
