import math
import random
from typing import List, Tuple, Optional
import time

class BezierCalculator:
    """Calculator for Bezier curves"""
    
    @staticmethod
    def factorial(n: int) -> int:
        """Calculate factorial of n"""
        if n < 0:
            return -1  # Indicate error
        result = 1
        for i in range(2, n + 1):
            result *= i
        return result

    @staticmethod
    def binomial(n: int, k: int) -> float:
        """Calculate binomial coefficient"""
        return float(BezierCalculator.factorial(n)) / (
            BezierCalculator.factorial(k) * BezierCalculator.factorial(n - k)
        )

    @staticmethod
    def bernstein_polynomial_point(x: float, i: int, n: int) -> float:
        """Calculate Bernstein polynomial point"""
        return BezierCalculator.binomial(n, i) * math.pow(x, i) * math.pow(1 - x, n - i)

    @staticmethod
    def bernstein_polynomial(points: List[Tuple[float, float]], t: float) -> List[float]:
        """Calculate Bernstein polynomial for given points and parameter t"""
        n = len(points) - 1
        x = 0.0
        y = 0.0
        for i in range(n + 1):
            bern = BezierCalculator.bernstein_polynomial_point(t, i, n)
            x += points[i][0] * bern
            y += points[i][1] * bern
        return [x, y]

    @staticmethod
    def calculate_points_in_curve(n_points: int, points: List[Tuple[float, float]]) -> List[List[float]]:
        """Calculate points along the Bezier curve"""
        curve_points = []
        for i in range(n_points):
            t = float(i) / (n_points - 1)
            curve_points.append(BezierCalculator.bernstein_polynomial(points, t))
        return curve_points


class HumanizeMouseTrajectory:
    """Human-like mouse movement generator"""
    
    def __init__(self, from_point: Tuple[float, float], to_point: Tuple[float, float]):
        self.from_point = from_point
        self.to_point = to_point
        self.points = []
        self.random_engine = random.Random(time.time())
        self.generate_curve()

    def get_points(self) -> List[int]:
        """Get flattened list of points as integers"""
        flat_points = []
        for point in self.points:
            flat_points.append(int(round(point[0])))
            flat_points.append(int(round(point[1])))
        return flat_points

    def generate_curve(self) -> None:
        """Generate the human-like curve"""
        left_boundary = min(self.from_point[0], self.to_point[0]) - 80.0
        right_boundary = max(self.from_point[0], self.to_point[0]) + 80.0
        down_boundary = min(self.from_point[1], self.to_point[1]) - 80.0
        up_boundary = max(self.from_point[1], self.to_point[1]) + 80.0

        internal_knots = self.generate_internal_knots(
            left_boundary, right_boundary, down_boundary, up_boundary, 2
        )

        curve_points = self.generate_points(internal_knots)
        curve_points = self.distort_points(curve_points, 1.0, 1.0, 0.5)
        self.points = self.tween_points(curve_points)

    def ease_out_quad(self, n: float) -> float:
        """Quadratic ease-out function"""
        if not 0.0 <= n <= 1.0:
            raise ValueError("Argument must be between 0.0 and 1.0")
        return -n * (n - 2)

    def generate_internal_knots(
        self, l_boundary: float, r_boundary: float, d_boundary: float, 
        u_boundary: float, knots_count: int
    ) -> List[Tuple[float, float]]:
        """Generate internal knots for the curve"""
        if not all(self.is_numeric(x) for x in [l_boundary, r_boundary, d_boundary, u_boundary]):
            raise ValueError("Boundaries must be numeric values")
        if knots_count < 0:
            raise ValueError("knots_count must be non-negative")
        if l_boundary > r_boundary:
            raise ValueError("Left boundary must be less than or equal to right boundary")
        if d_boundary > u_boundary:
            raise ValueError("Down boundary must be less than or equal to upper boundary")

        knots_x = self.random_choice_doubles(l_boundary, r_boundary, knots_count)
        knots_y = self.random_choice_doubles(d_boundary, u_boundary, knots_count)

        knots = []
        for i in range(knots_count):
            knots.append((knots_x[i], knots_y[i]))
        return knots

    def random_choice_doubles(self, min_val: float, max_val: float, size: int) -> List[float]:
        """Generate random doubles in range"""
        choices = []
        for _ in range(size):
            choices.append(self.random_engine.uniform(min_val, max_val))
        return choices

    def generate_points(self, knots: List[Tuple[float, float]]) -> List[List[float]]:
        """Generate points along the curve"""
        if not self.is_list_of_points_tuple(knots):
            raise ValueError("Knots must be a valid list of points")

        mid_pts_cnt = int(max(
            abs(self.from_point[0] - self.to_point[0]),
            abs(self.from_point[1] - self.to_point[1]),
            2.0
        ))

        control_points = knots.copy()
        control_points.insert(0, self.from_point)
        control_points.append(self.to_point)

        return BezierCalculator.calculate_points_in_curve(mid_pts_cnt, control_points)

    def distort_points(
        self, points: List[List[float]], distortion_mean: float, 
        distortion_st_dev: float, distortion_frequency: float
    ) -> List[List[float]]:
        """Add distortion to points to make movement more human-like"""
        if not all(self.is_numeric(x) for x in [distortion_mean, distortion_st_dev, distortion_frequency]):
            raise ValueError("Distortions must be numeric")
        if not self.is_list_of_points_list(points):
            raise ValueError("Points must be a valid list of points")
        if not 0.0 <= distortion_frequency <= 1.0:
            raise ValueError("distortion_frequency must be in range [0,1]")

        distorted = [points[0]]

        for i in range(1, len(points) - 1):
            x = points[i][0]
            y = points[i][1]
            delta = 0.0
            if self.random_engine.random() < distortion_frequency:
                # Simulate normal distribution using uniform distribution
                delta = round(self.random_engine.gauss(distortion_mean, distortion_st_dev))
            distorted.append([x, y + delta])

        distorted.append(points[-1])
        return distorted

    def get_max_time(self) -> int:
        """Get maximum time for movement"""
        # For now, using default values since MaskConfig is not available
        # You can replace this with your configuration system
        return 150  # Default value

    def get_min_time(self) -> int:
        """Get minimum time for movement"""
        # For now, using default values since MaskConfig is not available
        # You can replace this with your configuration system
        return 0  # Default value

    def tween_points(self, points: List[List[float]]) -> List[List[float]]:
        """Interpolate points for smoother movement"""
        if not self.is_list_of_points_list(points):
            raise ValueError("List of points not valid")

        # Calculate total length of the path
        total_length = 0.0
        for i in range(1, len(points)):
            dx = points[i][0] - points[i - 1][0]
            dy = points[i][1] - points[i - 1][1]
            total_length += math.sqrt(dx * dx + dy * dy)

        # Use power scale to keep speed consistent
        target_points = min(
            self.get_max_time(),
            max(self.get_min_time() + 2, int(math.pow(total_length, 0.25) * 20))
        )

        res = []
        for i in range(target_points):
            t = float(i) / (target_points - 1)
            eased_t = self.ease_out_quad(t)
            index = int(eased_t * (len(points) - 1))
            res.append(points[index])

        return res

    def is_numeric(self, val: float) -> bool:
        """Check if value is numeric"""
        return not math.isnan(val)

    def is_list_of_points_tuple(self, points: List[Tuple[float, float]]) -> bool:
        """Check if list contains valid points (tuple format)"""
        for p in points:
            if not self.is_numeric(p[0]) or not self.is_numeric(p[1]):
                return False
        return True

    def is_list_of_points_list(self, points: List[List[float]]) -> bool:
        """Check if list contains valid points (list format)"""
        for p in points:
            if len(p) != 2 or not self.is_numeric(p[0]) or not self.is_numeric(p[1]):
                return False
        return True

    async def click(self, xpath):
            while True:
                element = await self.page.wait_for_selector(xpath) 

                await element.scroll_into_view_if_needed()

                bounding_box = await element.bounding_box()

                if bounding_box:
                    x = bounding_box['x']
                    y = bounding_box['y']


                    center_width = bounding_box['width'] / 2
                    center_height = bounding_box['height'] / 2
                    new_x = bounding_box['x'] + center_width
                    new_y = bounding_box['y'] + center_height

                    trajectory = HumanizeMouseTrajectory(self.last_coords, (new_x, new_y))

                    points = trajectory.get_points()

                    for i in range(0, len(points), 2):
                        await self.page.mouse.move(points[i], points[i+1])
                    self.last_coords = (points[i], points[i+1])

                    bounding_box = await element.bounding_box()
                    if bounding_box:
                        if not bounding_box['x'] == x or not bounding_box['y'] == y:
                            continue

                    await self.page.click(xpath, position={'x': center_width, 'y': center_height})
               
                    break




