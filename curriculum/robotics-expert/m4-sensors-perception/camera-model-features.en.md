---
id: m4-camera-model-features
lang: en
title: Camera model, calibration, and image features
summary: Project 3D points to pixels with the pinhole camera model, learn how calibration estimates the intrinsic parameters by least squares, and detect image features such as Harris corners.
objectives:
  - Project a 3D point to pixel coordinates using the intrinsic matrix K and the extrinsic parameters [R|t].
  - Explain what calibration estimates (focal length, principal point, distortion coefficients) and how.
  - Compute the Harris corner response from image gradients and tell corners, edges, and flat regions apart.
tags: [camera, pinhole, calibration, features, harris, computer-vision]
---

# Camera model, calibration, and image features

A camera is a cheap, information-rich sensor, but it flattens the 3D world into a
2D image. This lesson writes down the rule for that (the pinhole model) as a
matrix, covers how to measure that matrix (calibration), and how to pick points
that are easy to find again (features). The point clouds of the next lesson and
the 3D localization of the last one both run on top of this model.

## Concepts

### The pinhole model

A point $(X, Y, Z)$ in camera coordinates (with the optical axis along $z$) is
imaged along the ray through the origin. First divide by $Z$ to get the
**normalized image coordinates** $(x, y) = (X/Z, Y/Z)$, then apply the focal
lengths in pixels $f_x, f_y$ and the principal point $(c_x, c_y)$ to get the pixel
$(u, v)$. A point in world coordinates is first moved into camera coordinates by
the extrinsic parameters $[R \mid t]$. The moment you divide by $Z$, depth is
gone, so a single camera can only tell you the **ray** a point lies on. Real
lenses also bend straight lines; the largest component is **radial distortion**
(coefficients $k_1, k_2, \dots$), which grows with distance from the center.

### Calibration

Calibration measures $K$ and the distortion coefficients. Photograph a checkerboard
of known size from several angles and minimize the **reprojection error** between
the 3D corner coordinates and the detected pixel coordinates (Zhang's method,
OpenCV `calibrateCamera`). The example below is a miniature version that assumes
the 3D points are known and solves for $f_x, c_x$ by linear least squares.

### Image features

A **feature point** is one you can find again when the same scene is photographed
from a different position. A flat region looks the same wherever you shift it, and
an edge is distinguishable in only one direction. A **corner** changes brightness
in every direction, so its position is pinned down. The Harris detector declares a
corner when both eigenvalues of the gradient covariance $M$ over a small window
are large. Straight lines (lane markings, wall edges) are found with the Hough
transform, and descriptors such as SIFT and ORB match feature points between
images.

## Key formulas

$$\begin{bmatrix} u \\ v \\ 1 \end{bmatrix} \sim
K\,[R \mid t]\begin{bmatrix} X_w \\ 1 \end{bmatrix},\qquad
K = \begin{bmatrix} f_x & 0 & c_x \\ 0 & f_y & c_y \\ 0 & 0 & 1 \end{bmatrix}$$

Radial distortion: $x_d = x\,(1 + k_1 r^2 + k_2 r^4)$, $r^2 = x^2 + y^2$ (and the
same for $y$).

The Harris response (sums over a window $W$, with $k \approx 0.04$-$0.06$):

$$M = \sum_W \begin{bmatrix} I_x^2 & I_x I_y \\ I_x I_y & I_y^2 \end{bmatrix},\qquad
R = \det M - k\,(\operatorname{tr} M)^2$$

A large positive $R$ means a corner, $R < 0$ an edge, and $|R| \approx 0$ a flat
region.

## Example

```python
import numpy as np

rng = np.random.default_rng(2)
K = np.array([[600.0, 0, 320], [0, 600.0, 240], [0, 0, 1]])


def project(K, R, t, P_w, k1=0.0):
    P_c = P_w @ R.T + t  # world -> camera coordinates
    x, y = P_c[:, 0] / P_c[:, 2], P_c[:, 1] / P_c[:, 2]  # normalized image coordinates
    s = 1 + k1 * (x**2 + y**2)  # radial distortion (first-order term only)
    return np.c_[K[0, 0] * s * x + K[0, 2], K[1, 1] * s * y + K[1, 2]]


# 1) Projection: the four corners of a 0.5 m square placed 2 m in front of the camera
R, t = np.eye(3), np.array([0.0, 0.0, 2.0])
square = np.array([[-0.25, -0.25, 0], [0.25, -0.25, 0], [0.25, 0.25, 0], [-0.25, 0.25, 0]])
print("pixel coordinates:\n", project(K, R, t, square).round(1))

# 2) Mini calibration: estimate fx, fy, cx, cy from 3D camera points and observed pixels
P_c = rng.uniform([-1, -1, 2], [1, 1, 5], (50, 3))
uv = project(K, np.eye(3), np.zeros(3), P_c) + rng.normal(0, 0.5, (50, 2))
x, y = P_c[:, 0] / P_c[:, 2], P_c[:, 1] / P_c[:, 2]
ones = np.ones_like(x)
fx, cx = np.linalg.lstsq(np.c_[x, ones], uv[:, 0], rcond=None)[0]
fy, cy = np.linalg.lstsq(np.c_[y, ones], uv[:, 1], rcond=None)[0]
print(f"estimated fx={fx:.1f}, fy={fy:.1f}, cx={cx:.1f}, cy={cy:.1f}")


# 3) Harris corners: a synthetic image with a bright rectangle
img = np.zeros((40, 40))
img[10:30, 12:28] = 1.0


def filter2(a, k):  # 2D correlation, edges padded by replication
    p = np.pad(a, k.shape[0] // 2, mode="edge")
    win = np.lib.stride_tricks.sliding_window_view(p, k.shape)
    return np.einsum("ijkl,kl->ij", win, k)


Ix = filter2(img, np.array([[-1, 0, 1], [-2, 0, 2], [-1, 0, 1]]) / 8)
Iy = filter2(img, np.array([[-1, -2, -1], [0, 0, 0], [1, 2, 1]]) / 8)
box = np.ones((5, 5))
Sxx, Syy, Sxy = filter2(Ix * Ix, box), filter2(Iy * Iy, box), filter2(Ix * Iy, box)
Rh = (Sxx * Syy - Sxy**2) - 0.05 * (Sxx + Syy) ** 2
for name, (r, c) in {"corner": (10, 12), "edge": (20, 12), "flat": (20, 20)}.items():
    print(f"{name:6s} ({r:2d},{c:2d}) R = {Rh[r, c]:+.4f}")
```

The square lands on pixels (245, 165)-(395, 315), since $600 \times 0.25 / 2 = 75$.
The intrinsics are recovered to within a pixel, and the Harris response is
positive at the corner, negative at the edge, and zero in the flat region.

**Exercise:** (1) predict how the pixel size changes when the square moves to 4 m
from the camera, then check it. (2) Project and plot a grid of points with
`k1=-0.2` to observe barrel distortion. (3) Plot the whole Harris response map as
an image and keep only the four corners using a threshold and 3×3 local maxima.

## Self-check questions

1. Use the projection equation to explain why a single pixel from one camera cannot fix the position of a 3D point.
2. Why must the checkerboard be photographed from several angles during calibration?
3. When the two eigenvalues of the Harris matrix $M$ are (large, large), (large, small), and (small, small), what kind of region is it in each case?

## How to study this stage

1. **Videos (first):** watch the Camera & Imaging series of Nayar's *First Principles of Computer Vision* for projection and lenses, then the Features & Boundaries series for corner and edge detection.
2. **Review:** if homogeneous coordinates feel hazy, rewatch Stachniss's *Homogeneous Coordinates*.
3. **This lesson plus the example:** compute one projected point by hand and match it against the code.
4. **Problems:** take the quiz in the Korean original (`rc quiz m4-camera-model-features`), then do exercises (1) through (3). Exercise (3) also connects to the neighbor search in the next lesson.
5. **Optional reinforcement:** the 3D Vision lessons at QUT Robot Academy, and the calibration chapter of Szeliski's textbook.

## References

- Shree Nayar, *First Principles of Computer Vision* — <https://fpcv.cs.columbia.edu/>
- Cyrill Stachniss, "Homogeneous Coordinates" — <https://www.youtube.com/watch?v=MQdm0Z_gNcw>
- QUT Robot Academy (Peter Corke) — <https://robotacademy.net.au/>
- Richard Szeliski, *Computer Vision: Algorithms and Applications* — the calibration and feature detection chapters.
