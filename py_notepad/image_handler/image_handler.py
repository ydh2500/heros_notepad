class ImageHandler:
    def __init__(self):
        self._original_images = {}

    def add_image(self, image_id, image):
        self._original_images[image_id] = image

    def get_image(self, image_id):
        return self._original_images.get(image_id)

    def update_image(self, image_id, updated_image):
        if image_id in self._original_images:
            self._original_images[image_id] = updated_image
            return updated_image
        else:
            print(f"Image with ID: {image_id} not found in original images.")
            return None