from evaluate.utils.database import get_shoe_images_by_ids
from evaluate.models import ShoeImage, ShoeMetadata
from evaluate.utils.serializer import ShoeMetadataAndImageSerializer, ShoeMetadataAndImagesSerializer


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

def convert_imageID_confidence_pairs_to_shoe_confidence(id_confidence_pairs):
    image_ids = []
    shoe_confidences = []
    for pair in id_confidence_pairs:
        image_ids.append(pair['shoeImageID'])
        shoe_confidences.append(pair['similarity'])

    shoe_confidence_pairs = []
    for i in range(len(image_ids)):
        shoe = ShoeImage.objects.select_related('shoe').get(id=image_ids[i]).shoe
        serialized_shoe = ShoeMetadataAndImagesSerializer(shoe).data
        shoe_confidence_pairs.append({
            'shoe': serialized_shoe,
            'confidence': shoe_confidences[i]
        })

    return shoe_confidence_pairs