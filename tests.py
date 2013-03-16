import unittest
from simple_units.base import (BaseDimension, _fill_relational_table,
                               UnitSystem, InvalidType, InvalidExpressionException)

us = UnitSystem()
Meter = us.new_dimension("Length", "Meter")
Second= us.new_dimension("Time", "Second")
#Minute = Second.dimension.add_unit(60 * Second, "Minute")
Length = Meter.dimension
Meter_2 = us.add_derived_dimension(Length * Length, "Area", "Meter^2")

print Meter(1)
print Meter_2(1)
Feet = us.add_unit("Feet", Meter / 3.208)
print Meter(1), Meter(1).convert_to(Feet)
class TestUnits(unittest.TestCase):


    def test_conversion(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Feet = us.add_unit("Feet", Meter / 3.208)
        Yard = us.add_unit("Yard", Feet * 3)

        f, m = Feet(3.208), Meter(1)
        print f.real_quantity, m.real_quantity
        self.assertAlmostEqual(f.real_quantity,m.real_quantity)
        self.assertUnitAlmostEqual(f,m)
        self.assertAlmostEqual(Feet(3), Yard(1))
        self.assertAlmostEqual(Feet(3), Feet(1) * 3)
        self.assertAlmostEqual(Feet(3), 3 * Feet(1))
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)

    def test_convert_to(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Feet = us.add_unit("Feet", Meter / 3.208)
        Yard = us.add_unit("Yard", Feet * 3)

        self.assertUnitAlmostEqual(Feet(1), Feet(1).convert_to(Meter))

        self.assertAlmostEqual(Feet(3), Yard(1))
        self.assertAlmostEqual(Feet(3), Feet(1) * 3)
        self.assertAlmostEqual(Feet(3), 3 * Feet(1))
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)
        self.assertAlmostEqual(Feet(1),  Feet(3) / 3)

    def test_derived_dimension_unit(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter")
        Second = us.new_dimension("Time", "Second")

        Length = us.Dimensions.Length
        Msq = us.add_derived_dimension(Length * Length, "Area", "Meter^2")

        self.assertAlmostEqual(
            Meter(10), (Msq(100) / Meter(10)))

        Area = us.Dimensions.Area
        Mcb = us.add_derived_dimension(Area * Length, "Volume", "Meter^3")

        self.assertAlmostEqual(
            Msq(100), Mcb(1000)/(Meter(10)))

    def assertUnitAlmostEqual(self, first, second,
                          places=None, msg=None, delta=None):
        """Fail if the two objects are unequal as determined by their
           difference rounded to the given number of decimal places
           (default 7) and comparing to zero, or by comparing that the
           between the two objects is more than the given delta.

           Note that decimal places (from zero) are usually not the same
           as significant digits (measured from the most signficant digit).

           If the two objects compare equal then they will automatically
           compare almost equal.
        """
        if first == second:
            # shortcut
            return
        if delta is not None and places is not None:
            raise TypeError("specify delta or places not both")

        if delta is not None:
            if abs(first - second) <= delta:
                return

            standardMsg = '%s != %s within %s delta' % (safe_repr(first),
                                                        safe_repr(second),
                                                        safe_repr(delta))
        else:
            if places is None:
                places = 7

            abs_ = abs(second.real_quantity - first.real_quantity)
            if round(abs_, places) == 0:
                return

            standardMsg = '%s != %s within %r places' % (safe_repr(first),
                                                          safe_repr(second),
                                                          places)
        msg = self._formatMessage(msg, standardMsg)
        raise self.failureException(msg)

class TestDimensions(unittest.TestCase):

    def test_fill(self):
        mult_table = {"Length*Length":"Area", "Area":"Area", "Length":"Length"}
        n_table = _fill_relational_table(mult_table)
        self.assertEquals(len(n_table.keys()), 4)
        self.assertTrue("Area/Length" in n_table.keys())
        self.assertEquals(n_table['Area/Length'], 'Length')

        div_table = {"Length/Time":"Speed", "Length":"Length",
                     "Time":"Time", "Speed":"Speed"}
        nd_table = _fill_relational_table(div_table)
        self.assertEquals(
            len(nd_table.keys()), 5)
        self.assertTrue(
            "Speed*Time" in nd_table.keys())
        self.assertEquals(nd_table['Speed*Time'], 'Length')


    def test_instatiation(self):
        class LLength(BaseDimension):
            us = UnitSystem()
            Meter = us.new_dimension("Length", "Meter",)
            Meter(10)

    def test_equality(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter",)
        self.assertEquals(
            Meter(10), Meter(10))
    def test_like_addition(self):
        us = UnitSystem()
        LLength = us.new_dimension("LLength", "Meter")
        expected20 = LLength(10) + LLength(10)
        self.assertEquals(expected20, LLength(20))
    def test_unlike_addition(self):
        us = UnitSystem()
        LLength = us.new_dimension("LLength", "Meter")
        LTime = us.new_dimension("LTime", "Second")
        def unlike():
            no_answer = LLength(10) + LTime(20)
        self.assertRaises(InvalidType, unlike)

    def test_multiply(self):
        us = UnitSystem()
        Meter = us.new_dimension("Length", "Meter",)
        Length = Meter.dimension
        Msq = us.add_derived_dimension(Length * Length, "Area", "Meter^2")
        self.assertEquals(
            Meter(10) * Meter(10), Msq(100))

if __name__ == "__main__":
    unittest.main()
