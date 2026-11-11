---
id: m4-object-detection-intro
lang: en
title: Introduction to deep-learning object detection
summary: Learn what a CNN detector takes in and puts out, how to post-process and evaluate that output with IoU, NMS, and precision/recall, and how to turn a 2D detection into a 3D position with depth and the camera model.
objectives:
  - Explain the input and output structure (boxes, classes, scores) of a convolutional object detector.
  - Implement IoU and NMS and evaluate detections with precision and recall.
  - Back-project a 2D detection box and a depth value through the camera intrinsics to get the object's 3D position.
tags: [deep-learning, object-detection, cnn, iou, nms, perception]
---

# Introduction to deep-learning object detection

The previous lessons extracted geometry — corners, planes, point clouds — by hand.
This lesson covers the part where a learned model answers "what is where," and,
more importantly for a robot, how to turn that answer into something an arm or a
base can act on.

## Concepts

### What a CNN detector takes in and puts out

The input is an image tensor (height × width × 3). A convolution layer slides a
small kernel — like the Sobel filter of the previous lesson — across the whole
image, except that the kernel values are learned from data rather than chosen by a
person. As layers get deeper, the feature maps become more abstract: edges →
corners and textures → parts → objects.

A detector (the YOLO family and others) outputs hundreds to thousands of candidate
boxes, each with a **box** $[x_1, y_1, x_2, y_2]$, a **class**, and a **confidence
score**. Because several overlapping boxes appear on the same object,
post-processing is required. Segmentation models output per-pixel masks instead of
boxes.

### Post-processing: IoU and NMS

- **IoU (Intersection over Union):** the area of the intersection of two boxes divided by the area of their union, between 0 and 1.
- **NMS (Non-Maximum Suppression):** keep the highest-scoring box and delete every box whose IoU with it exceeds a threshold (typically 0.5). Repeat on what remains.
- **Score threshold:** discard low-scoring boxes. Lowering it misses fewer objects and produces more false detections.

### Evaluation: precision and recall

A detection that pairs with a ground-truth box at IoU ≥ 0.5 is a true positive
(TP), otherwise a false positive (FP); an unmatched ground-truth box is a false
negative (FN). The area under the precision-recall curve traced out by sweeping
the score threshold is AP, and the mean over classes is mAP. In robotics the
priority depends on the use: missing an object means a collision (recall matters),
while a wrong detection means grasping the wrong thing (precision matters).

### From 2D detection to 3D position

A detection box is only pixel coordinates. For an arm to grasp a cup, it needs a
3D position in meters. Back-project the depth $Z$ at the box center through the
intrinsics $K$ to get a 3D point in camera coordinates, then move it into the
robot frame with the transforms of M1. Reflective and transparent objects may
have missing depth values, so taking the median of the depths inside the box is
safer (the same outlier story as the first lesson of M4).

## Key formulas

$$\mathrm{IoU}(A, B) = \frac{|A \cap B|}{|A| + |B| - |A \cap B|}$$

$$\text{precision} = \frac{TP}{TP + FP},\qquad \text{recall} = \frac{TP}{TP + FN}$$

Back-projection (pixel $(u, v)$, depth $Z$):

$$P_c = Z\,K^{-1}\begin{bmatrix} u \\ v \\ 1 \end{bmatrix}
= \begin{bmatrix} (u - c_x)\,Z/f_x \\ (v - c_y)\,Z/f_y \\ Z \end{bmatrix}$$

## Example

Run NMS, evaluation, and 3D position estimation on an assumed detector output. In
practice you put the model's output into `boxes` and `scores`.

```python
import numpy as np


def area(r):
    return (r[2] - r[0]) * (r[3] - r[1])


def iou(a, b):  # box: [x1, y1, x2, y2]
    w = max(0.0, min(a[2], b[2]) - max(a[0], b[0]))
    h = max(0.0, min(a[3], b[3]) - max(a[1], b[1]))
    inter = w * h
    return inter / (area(a) + area(b) - inter)


def nms(boxes, scores, thresh=0.5):
    order, keep = list(np.argsort(scores)[::-1]), []
    while order:
        i = order.pop(0)
        keep.append(int(i))
        order = [j for j in order if iou(boxes[i], boxes[j]) < thresh]
    return keep


# Detector output (assumed): several boxes on the same cup plus other objects
boxes = np.array(
    [
        [100, 100, 200, 220],
        [105, 98, 205, 225],
        [95, 110, 190, 215],
        [300, 150, 380, 260],
        [500, 50, 540, 90],
    ],
    dtype=float,
)
scores = np.array([0.92, 0.85, 0.60, 0.88, 0.30])
keep = nms(boxes, scores)
print("boxes left after NMS:", keep)

# Compare with ground truth: IoU >= 0.5 counts as a true positive (TP)
gt = np.array([[102, 102, 202, 222], [310, 150, 385, 255]], dtype=float)
matched, tp = set(), 0
for i in keep:  # keep is in descending score order
    ious = [iou(boxes[i], g) for g in gt]
    j = int(np.argmax(ious))
    if ious[j] >= 0.5 and j not in matched:
        matched.add(j)
        tp += 1
print(f"precision {tp / len(keep):.2f}, recall {tp / len(gt):.2f}")

# 2D box + depth -> 3D position (pinhole back-projection)
K = np.array([[600.0, 0, 320], [0, 600.0, 240], [0, 0, 1]])
x1, y1, x2, y2 = boxes[keep[0]]
u, v, depth = (x1 + x2) / 2, (y1 + y2) / 2, 1.2  # depth sensor value [m]
P_c = depth * np.linalg.inv(K) @ np.array([u, v, 1.0])
print("cup center (camera coordinates) [m]:", P_c.round(3))
```

NMS keeps only the 0.92 box out of the three overlapping ones on the cup, giving
`[0, 3, 4]`. Box 4 is a false detection with no ground truth, so precision is 0.67
and recall is 1.00. Applying a score threshold of 0.5 first brings precision to
1.00 as well. The cup center sits 0.34 m to the left, 0.16 m above, and 1.2 m in
front of the camera.

**Exercise:** (1) sweep the score threshold from 0 to 1, compute precision and
recall, and plot the curve. (2) Explain how the result changes when the NMS
threshold is set to 0.3 and to 0.8. (3) Build an array of depth values inside a
box (with some zeros standing for failed measurements) and write a median-based 3D
position estimator.

## Self-check questions

1. Why is NMS needed on detector output, and what goes wrong if the NMS threshold is too low?
2. For an obstacle-avoidance detector and for a grasping detector, which matters more, precision or recall?
3. Why can a 2D box alone not give an object's 3D position, and what are two sensors that fill the gap?

## How to study this stage

1. **Textbook (first):** read Tedrake's *Robotic Manipulation* Ch. 9 for the big picture of how detection and segmentation results are used on a robot, and skim Ch. 10, Deep Perception.
2. **This lesson plus the example:** compute one IoU by hand and match it against the code.
3. **Problems:** take the quiz in the Korean original (`rc quiz m4-object-detection-intro`), then do exercises (1) through (3). Plotting the curve builds a feel for choosing thresholds.
4. **Optional practice:** if you know PyTorch, download a pretrained detector and feed its output boxes into this lesson's post-processing code. For a Korean-language practical course, see Fastcampus Physical AI Part 2.
5. **Wrap-up:** review where the coordinate transforms, noise models, and camera model of M1-M4 were reused.

## References

- Russ Tedrake, *Robotic Manipulation*, Ch. 9-10 — <https://manipulation.mit.edu/>
- Shree Nayar, *First Principles of Computer Vision* — <https://fpcv.cs.columbia.edu/>
- Fastcampus, "Physical AI 입문 All-In-One" (in Korean) — <https://fastcampus.co.kr/data_online_physicalai>
