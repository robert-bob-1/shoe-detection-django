from evaluate.utils.database import get_shoe_images_by_ids


def convert_id_confidence_pairs_to_image_confidence(id_confidence_pairs):
    image_ids = []
    image_confidences = []
    for pair in id_confidence_pairs:
        image_ids.append(pair['shoeImageID'])
        image_confidences.append(pair['similarity'])

    binary_images = get_shoe_images_by_ids(image_ids)

    image_confidence_pairs = []
    for i in range(len(binary_images)):
        image_confidence_pairs.append({
            'image': binary_images[i],
            'confidence': image_confidences[i]
        })

    return image_confidence_pairs