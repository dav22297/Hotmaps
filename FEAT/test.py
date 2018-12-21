import numpy as np


def normalize(vector):
    return vector/np.linalg.norm(vector)


def intersection_line(plane1, plane2):
    if np.dot(plane1.normal_vector, plane2.normal_vector) != 0:
        q = plane1.origin + (np.linalg.norm(plane2.origin) - np.dot(plane2.normal_vector, plane1.origin)) / \
            np.dot(plane2.normal_vector, plane1.v1) * plane1.v1
        w = plane1.v2 - np.dot(plane2.normal_vector, plane1.v2) / np.dot(plane2.normal_vector, plane1.v1) * plane1.v1
    else:
        raise ArithmeticError("Planes are parallel, can not compute a intersection line")
    return Line(w, q)


class Plane:

    def __init__(self, p1=None, p2=None, p3=None, v1=None, v2=None, normal_vector=None, origin=None):
        if p1 is not None and p2 is not None and p3 is not None:
            if p1 != p2 and p1 != p3 and p2 != p3:
                self.p1 = np.array(p1)
                self.p2 = np.array(p2)
                self.p3 = np.array(p3)
                self.point_to_vector()
                self.vector_to_normal()
            else:
                raise ArithmeticError("cant construct a plane with two equal points")

        elif v1 is not None and v2 is not None and origin is not None:

            self.v1 = normal_vector(np.array(v1))
            self.v2 = normalize(np.array(v2))
            self.origin = np.array(origin)
            self.vector_to_point()
            self.vector_to_normal()

        elif normal_vector is not None and origin is not None:
            self.normal_vector = normalize(np.array(normal_vector))
            self.origin = np.array(origin)
            self.normal_to_vector()
            self.vector_to_point()

        else:
            raise AttributeError("Initialize with p1,p2,p3 or v1,v2,origin or normal_vector,origin. If more than one of"
                                 "the three sets are given the first one in the order mentioned is used")

    def point_to_vector(self):
        self.v1 = normalize(self.p2 - self.p1)
        self.v2 = normalize(self.p3 - self.p1)
        self.origin = self.p1

    def vector_to_normal(self):
        self.normal_vector = normalize(np.cross(self.v1, self.v2))

    def vector_to_point(self):
        self.p1 = self.v1 + self.origin
        self.p2 = self.v2 + self.origin
        self.p3 = self.origin

    def normal_to_vector(self):
        x = np.array([1, 0, 0])
        y = np.array([0, 1, 0])
        if not np.array_equal(self.normal_vector, x):
            v1 = x
        else:
            v1 = y
        v1 = v1 - v1.dot(self.normal_vector) * self.normal_vector / np.linalg.norm(self.normal_vector) ** 2
        self.v1 = normalize(v1)
        self.v2 = normalize(np.cross(self.normal_vector, self.v1))

    def intersection_line(self, plane):
        if np.dot(self.normal_vector, plane.normal_vector) != 0:
            q = self.origin + (np.linalg.norm(plane.origin) - np.dot(plane.normal_vector, self.origin)) / \
                np.dot(plane.normal_vector, self.v1) * self.v1
            w = self.v2 - np.dot(plane.normal_vector, self.v2)/np.dot(plane.normal_vector, self.v1) * self.v1
        else:
            raise ArithmeticError("Planes are parallel, can not compute a intersection line")
        return Line(w, q)

    def set_normal(self, normal_vector):
        self.normal_vector = normal_vector
        self.normal_to_vector()
        self.vector_to_point()

    def set_origin(self, origin):
        self.origin = origin
        self.normal_to_vector()
        self.vector_to_point()


class Line:

    def __init__(self, vector, origin):
        self.vector = vector
        self.origin = origin



Plane(p1=(0,0,0), p2=(1,0,0), p3=(1,2,1))