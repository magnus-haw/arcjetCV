import numpy as np
import cv2


class GrabcutSegmenter:
    """
    GrabcutSegmenter uses OpenCV's GrabCut algorithm to segment foreground objects from the background.
    """

    def __init__(self):
        """
        Initializes the GrabcutSegmenter.
        """
        self.mask = None
        self.bgdModel = np.zeros((1, 65), np.float64)
        self.fgdModel = np.zeros((1, 65), np.float64)

    def apply_grabcut(self, image, rect):
        """
        Applies the GrabCut algorithm to segment the foreground from the background in an image.

        Parameters:
        - image: The image on which to apply GrabCut segmentation (numpy array).
        - rect: The rectangle (x, y, width, height) defining the foreground object.

        Returns:
        - A mask indicating the foreground and background.
        """
        # Initialize the mask
        if self.mask is None or self.mask.shape[:2] != image.shape[:2]:
            self.mask = np.zeros(image.shape[:2], dtype=np.uint8)

        # Apply GrabCut
        cv2.grabCut(
            image,
            self.mask,
            rect,
            self.bgdModel,
            self.fgdModel,
            5,
            cv2.GC_INIT_WITH_RECT,
        )

        # Convert the mask to binary format
        binMask = np.where(
            (self.mask == cv2.GC_FGD) | (self.mask == cv2.GC_PR_FGD), 255, 0
        ).astype("uint8")

        return binMask

    def refine_segmentation(self, image, iterCount=5):
        """
        Refines the existing segmentation mask using further iterations of GrabCut.

        Parameters:
        - image: The image on which to refine segmentation (numpy array).
        - iterCount: The number of iterations for refinement.

        Returns:
        - A refined mask indicating the foreground and background.
        """
        if self.mask is None:
            print("Mask not initialized. Apply initial segmentation first.")
            return None

        # Apply GrabCut with the existing mask
        cv2.grabCut(
            image,
            self.mask,
            None,
            self.bgdModel,
            self.fgdModel,
            iterCount,
            cv2.GC_INIT_WITH_MASK,
        )

        # Convert the mask to binary format
        binMask = np.where(
            (self.mask == cv2.GC_FGD) | (self.mask == cv2.GC_PR_FGD), 255, 0
        ).astype("uint8")

        return binMask


# Example usage
if __name__ == "__main__":
    segmenter = GrabcutSegmenter()
    # Load your image
    image = cv2.imread("path/to/your/image.jpg")
    # Define initial foreground rectangle (x, y, width, height)
    rect = (50, 50, 450, 290)
    initial_mask = segmenter.apply_grabcut(image, rect)
    # Optionally refine the segmentation
    refined_mask = segmenter.refine_segmentation(image, iterCount=5)
