import torch
import numpy as np
from torchvision.transforms import Compose, ToTensor, Normalize
from segment_anything import sam_model_registry, SamPredictor
from segment_anything import sam_model_registry, SamAutomaticMaskGenerator, SamPredictor
import os
from matplotlib.lines import Line2D
import pickle


class SAMSegmenter:
    def __init__(self, img, filePath, matplotlib_widget):
        self.matplotlib_widget = matplotlib_widget
        # self.sam_checkbox.setChecked(True)
        self.img = img
        self.min_mask_region_area = 100
        self.sam = sam_model_registry["vit_h"](
            checkpoint="segmentation_gui/sam_vit_h_4b8939.pth"
        )
        if torch.cuda.is_available():
            self.sam.to(device="cuda")
        else:
            self.sam.to(device="cpu")
        self.auto_mask_generator = SamAutomaticMaskGenerator(
            self.sam,
            points_per_side=32,
            pred_iou_thresh=0.5,
            stability_score_thresh=0.5,
            crop_n_layers=1,
            crop_n_points_downscale_factor=2,
            min_mask_region_area=self.min_mask_region_area,
        )
        self.predictor = SamPredictor(self.sam)
        self.predictor.set_image(self.img)

        # Initialize the Matplotlib plot within the MatplotlibWidget
        self.matplotlib_widget.ax.clear()
        self.matplotlib_widget.plot_image(self.img)
        self.matplotlib_widget.ax.set_title(
            "Press 'h' to show/hide commands.", fontsize=10
        )
        self.matplotlib_widget.ax.autoscale(False)

        self.label = 1
        (self.add_plot,) = self.matplotlib_widget.ax.plot(
            [], [], "o", markerfacecolor="green", markeredgecolor="k", markersize=5
        )
        (self.rem_plot,) = self.matplotlib_widget.ax.plot(
            [], [], "x", markerfacecolor="red", markeredgecolor="red", markersize=5
        )
        self.color_set = set()
        self.current_color = self.pick_color()
        self.legend_elements = [
            Line2D(
                [0],
                [0],
                color=np.array(self.current_color) / 255,
                lw=2,
                label=f"Mask {self.label}\n",
            )
        ]
        # self.matplotlib_widget.ax.legend(handles=self.full_legend)
        self.add_xs, self.add_ys, self.rem_xs, self.rem_ys, self.trace = (
            [],
            [],
            [],
            [],
            [],
        )
        self.mask_data = np.zeros(
            (self.img.shape[0], self.img.shape[1], 4), dtype=np.uint8
        )
        for i in range(3):
            self.mask_data[:, :, i] = self.current_color[i]

        self.mask_plot = self.matplotlib_widget.ax.imshow(self.mask_data)

        self.prev_mask_data = np.zeros(
            (self.img.shape[0], self.img.shape[1], 4), dtype=np.uint8
        )
        self.prev_mask_plot = self.matplotlib_widget.ax.imshow(
            self.prev_mask_data, label=r"$y={}x$".format(self.label)
        )

        # Connect Matplotlib events to handling methods
        self.matplotlib_widget.canvas.mpl_connect("button_press_event", self._on_click)
        self.matplotlib_widget.canvas.mpl_connect("key_press_event", self._on_key)

        self.show_help_text = False
        self.help_text = self.matplotlib_widget.ax.text(2, 0, "", fontsize=10)
        self.full_legend = []
        self.opacity = 100  # out of 255
        self.global_masks = np.zeros(
            (self.img.shape[0], self.img.shape[1]), dtype=np.uint8
        )

        print("Generating automatic masks ... ", end="")
        masks = self.auto_mask_generator.generate(self.img)
        print("Done")
        # input_file = f"{str(self.img)}_mask.pkl"
        # input_path = os.path.join(input_folder, input_file)

        # with open(input_path, 'rb') as f:
        #     masks = pickle.load(f)

        with open("test.pkl", "wb") as f:
            pickle.dump(masks, f)

        # input_file = f"{os.path.splitext(filePath)[0]}.pkl"
        # self.filePath = filePath
        # print(input_file)
        # with open(input_file, "rb") as f:
        #     masks = pickle.load(f)

        max_n_masks = 10000
        self.auto_masks = np.zeros(
            (self.img.shape[0], self.img.shape[1], min(len(masks), max_n_masks)),
            dtype=bool,
        )
        for i in range(self.auto_masks.shape[2]):
            self.auto_masks[:, :, i] = masks[i]["segmentation"]

        # np.save("input/test.npy", self.auto_masks)
        # self.auto_masks = np.load("input/test.npy")

    def save_annotation(self, labels_file_outpath):
        dir_path = os.path.split(labels_file_outpath)[0]
        if dir_path != "" and not os.path.exists(dir_path):
            os.makedirs(dir_path)
        cv2.imwrite(labels_file_outpath, self.global_masks)

    def pick_color(self):
        while True:
            color = tuple(np.random.randint(low=0, high=255, size=3).tolist())
            if color not in self.color_set:
                self.color_set.add(color)
                return color

    def _on_key(self, event):
        if event.key == "z":
            self.undo()

        elif event.key == "enter":
            print("enter")
            self.new_tow()

        elif event.key == "h":
            if not self.show_help_text:
                self.help_text.set_text(
                    "• 'left click': select a point inside object to label\n"
                    "• 'right click': select a point to exclude from label\n"
                    "• 'enter': confirm current label and create new\n"
                    "• 'z': undo point\n"
                    "• 'esc': close and save"
                )
                self.help_text.set_bbox(
                    dict(facecolor="white", alpha=1, edgecolor="black")
                )
                self.show_help_text = True
            else:
                self.help_text.set_text("")
                self.show_help_text = False
            self.matplotlib_widget.canvas.draw()

    def _on_click(self, event):
        if event.inaxes != self.matplotlib_widget.ax and (event.button in [1, 3]):
            return
        x = int(np.round(event.xdata))
        y = int(np.round(event.ydata))

        if event.button == 1:  # left click
            self.trace.append(True)
            self.add_xs.append(x)
            self.add_ys.append(y)
            self.show_points(self.add_plot, self.add_xs, self.add_ys)

        else:  # right click
            self.trace.append(False)
            self.rem_xs.append(x)
            self.rem_ys.append(y)
            self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        self.get_mask()

    def show_points(self, plot, xs, ys):
        plot.set_data(xs, ys)
        self.matplotlib_widget.canvas.draw()

    def clear_mask(self):
        self.mask_data.fill(0)
        self.mask_plot.set_data(self.mask_data)
        self.matplotlib_widget.canvas.draw()

    def get_mask(self):
        add_compare = np.sum(self.auto_masks[self.add_ys, self.add_xs], axis=0)
        add_compare += np.sum(~self.auto_masks[self.rem_ys, self.rem_xs], axis=0)
        matches = np.where(add_compare == len(self.add_xs) + len(self.rem_xs))[0]

        found_match = False
        for match in matches:
            mask = self.auto_masks[:, :, match]
            if not np.any(np.logical_and(mask, self.global_masks)):
                found_match = True
                break

        if not found_match:
            # print("No matches in auto masks, calling single predictor")
            mask = self.generate_mask()
            mask[self.global_masks > 0] = 0
            mask = self.remove_small_regions(mask, self.min_mask_region_area, "holes")
            mask = self.remove_small_regions(mask, self.min_mask_region_area, "islands")

        self.mask_data[:, :, 3] = mask * self.opacity
        self.mask_plot.set_data(self.mask_data)
        self.matplotlib_widget.canvas.draw()

    def generate_mask(self):
        mask, _, _ = self.predictor.predict(
            point_coords=np.array(
                list(zip(self.add_xs, self.add_ys))
                + list(zip(self.rem_xs, self.rem_ys))
            ),
            point_labels=np.array([1] * len(self.add_xs) + [0] * len(self.rem_xs)),
            multimask_output=False,
        )
        return mask[0].astype(np.uint8)

    def undo(self):
        if len(self.trace) == 0:
            return

        if self.trace[-1]:
            self.add_xs = self.add_xs[:-1]
            self.add_ys = self.add_ys[:-1]
            self.show_points(self.add_plot, self.add_xs, self.add_ys)
        else:
            self.rem_xs = self.rem_xs[:-1]
            self.rem_ys = self.rem_ys[:-1]
            self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        self.trace.pop()

        if len(self.trace) != 0:
            self.get_mask()
        else:
            self.clear_mask()

    def new_tow(self):
        # clear points
        self.add_xs, self.add_ys, self.rem_xs, self.rem_ys, self.trace = (
            [],
            [],
            [],
            [],
            [],
        )
        self.show_points(self.add_plot, self.add_xs, self.add_ys)
        self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        mask = self.mask_data[:, :, 3] > 0
        self.global_masks[mask] = self.label
        self.label += 1

        self.prev_mask_data[:, :, :3][mask] = self.current_color
        self.prev_mask_data[:, :, 3][mask] = 255
        self.prev_mask_plot.set_data(self.prev_mask_data)

        self.legend_elements = [
            Line2D(
                [0],
                [0],
                color=np.array(self.current_color) / 255,
                lw=2,
                label=f"Mask {self.label-1}\n",
            )
        ]
        self.full_legend += self.legend_elements
        self.matplotlib_widget.ax.legend(handles=self.full_legend)
        self.matplotlib_widget.canvas.draw()

        self.current_color = self.pick_color()
        for i in range(3):
            self.mask_data[:, :, i] = self.current_color[i]
        self.clear_mask()

    def label_ok(self):
        # clear points
        self.add_xs, self.add_ys, self.rem_xs, self.rem_ys, self.trace = (
            [],
            [],
            [],
            [],
            [],
        )
        self.show_points(self.add_plot, self.add_xs, self.add_ys)
        self.show_points(self.rem_plot, self.rem_xs, self.rem_ys)

        mask = self.mask_data[:, :, 3] > 0
        self.global_masks[mask] = self.label

        self.prev_mask_data[:, :, :3][mask] = self.current_color
        self.prev_mask_data[:, :, 3][mask] = 255
        self.prev_mask_plot.set_data(self.prev_mask_data)
        self.matplotlib_widget.canvas.draw()

    @staticmethod
    def remove_small_regions(mask, area_thresh, mode):
        """Function from https://github.com/facebookresearch/segment-anything/blob/main/segment_anything/utils/amg.py"""
        assert mode in ["holes", "islands"]
        correct_holes = mode == "holes"
        working_mask = (correct_holes ^ mask).astype(np.uint8)
        n_labels, regions, stats, _ = cv2.connectedComponentsWithStats(working_mask, 8)
        sizes = stats[:, -1][1:]  # Row 0 is background label
        small_regions = [i + 1 for i, s in enumerate(sizes) if s < area_thresh]
        if len(small_regions) == 0:
            return mask
        fill_labels = [0] + small_regions
        if not correct_holes:
            fill_labels = [i for i in range(n_labels) if i not in fill_labels]
            # If every region is below threshold, keep largest
            if len(fill_labels) == 0:
                fill_labels = [int(np.argmax(sizes)) + 1]
        mask = np.isin(regions, fill_labels)
        return mask
