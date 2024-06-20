
from evaluate.models import ShoeClassification, ShoeImage


def save_image_classification_data(shoe_image_id, classification_data):
    # Save the classification data
    classification = ShoeClassification(
        shoe_image=ShoeImage.objects.get(id=shoe_image_id),
        boots_confidence=classification_data['boots'],
        flip_flops_confidence=classification_data['flip_flops'],
        loafers_confidence=classification_data['loafers'],
        sandals_confidence=classification_data['sandals'],
        sneakers_confidence=classification_data['sneakers'],
        soccer_shoes_confidence=classification_data['soccer_shoes']
    )

    print(f"Classification data: {classification}")


def save_product_classification_data(shoe_metadata, all_classification_data):
    #compute total confidence scores for each class
    confidence_scores_per_class = {}

    print(f"all_classification_data: {all_classification_data}")
    for classification_data in all_classification_data:
        for class_name, confidence in classification_data.items():
            if class_name not in confidence_scores_per_class:
                confidence_scores_per_class[class_name] = 0
            confidence_scores_per_class[class_name] += confidence
    print(f"confidence_scores_per_class: {confidence_scores_per_class}")

    # Find the class with the highest confidence score
    max_confidence = 0
    max_class = 'Unknown'
    for class_name, confidence in confidence_scores_per_class.items():
        print(f"{class_name}: {confidence}")
        if confidence > max_confidence:
            print(f"max_confidence: {confidence}; class: {class_name}")
            max_confidence = confidence
            max_class = class_name

    print(max_confidence, max_class)
    print("all classification data before saving: ", all_classification_data)

    shoe_metadata.classification = max_class
    shoe_metadata.classification_confidence = max_confidence/len(all_classification_data)

    shoe_metadata.save()

